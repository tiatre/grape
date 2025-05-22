#!/usr/bin/env python

# Import libraries
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Union, FrozenSet
import argparse
import csv
import logging
import networkx as nx
import numpy as np
from ete3 import Tree, TreeNode

# Import local modules
import common

# TODO: decide whether to cast resolution to int in community methods, because nx works with float (maybe for the steps?)

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class CommunityMethod:
    def __init__(self, graph: nx.Graph, weight: str):
        self.graph = graph
        self.weight = weight

    def find_communities(self, resolution: Union[float, int]) -> List[FrozenSet]:
        raise NotImplementedError("This method should be overridden by subclasses")


class GreedyModularity(CommunityMethod):
    def find_communities(self, resolution: Union[float, int]) -> List[FrozenSet]:
        community_generator = nx.algorithms.community.greedy_modularity_communities(
            self.graph, weight=self.weight, resolution=int(resolution)
        )
        return [frozenset(community) for community in community_generator]  # type: ignore


class LouvainCommunities(CommunityMethod):
    def find_communities(self, resolution: Union[float, int]) -> List[FrozenSet]:
        community_generator = nx.algorithms.community.louvain_communities(
            self.graph, weight=self.weight, resolution=int(resolution)
        )
        return [frozenset(community) for community in community_generator]  # type: ignore


class ParameterSearchStrategy:
    def initialize(self) -> float:
        raise NotImplementedError

    def update(self, current_value: float) -> float:
        raise NotImplementedError

    def should_stop(self, num_communities: int, target: int) -> bool:
        raise NotImplementedError


class FixedIncrementStrategy(ParameterSearchStrategy):
    def __init__(self, increment: float = 0.1):
        self.increment = increment

    def initialize(self) -> float:
        return 0.0

    def update(self, current_value: float) -> float:
        return current_value + self.increment

    def should_stop(self, num_communities: int, target: int) -> bool:
        return num_communities == target


class DynamicAdjustmentStrategy(ParameterSearchStrategy):
    def __init__(self, initial_value: float = 0.0, adjust_factor: float = 0.1):
        self.adjust_factor = adjust_factor
        self.value = initial_value

    def initialize(self) -> float:
        return self.value

    def update(self, current_value: float) -> float:
        # Dynamic adjustment logic can be implemented here
        # For simplicity, let's just increment by a variable factor
        self.value += self.adjust_factor * self.value
        return self.value

    def should_stop(self, num_communities: int, target: int) -> bool:
        return num_communities == target


class AdaptiveDynamicAdjustmentStrategy(ParameterSearchStrategy):
    def __init__(
        self,
        target: int,
        initial_value: float = 0.1,
        adjust_factor: float = 0.05,
    ):
        self.initial_value = initial_value
        self.adjust_factor = adjust_factor
        self.target = target
        self.value = initial_value
        self.previous_diff = None

    def initialize(self) -> float:
        return self.initial_value

    def update(self, current_value: float, current_communities: int) -> float:
        # Calculate the difference between the current number of communities and the target
        diff = abs(self.target - current_communities)

        # If this is the first update, initialize previous_diff
        if self.previous_diff is None:
            self.previous_diff = diff
            return current_value

        # Check if the number of communities is moving towards the target or not
        if diff < self.previous_diff:
            # We are getting closer to the target, increase the adjustment factor slightly
            self.adjust_factor *= 1.1
        else:
            # We are moving away from the target, decrease the adjustment factor and change direction
            self.adjust_factor *= -0.5

        self.previous_diff = diff
        self.value += self.adjust_factor
        return self.value

    def should_stop(self, num_communities: int, target: int) -> bool:
        return num_communities == target


def build_history(
    G: nx.Graph,
    num_languages: int,
    method: str = "greedy",
    strategy_name: str = "fixed",
    initial_value: float = 0.0,
    adjust_factor: float = 0.1,
) -> List[common.HistoryEntry]:

    # Obtain the community detection method based on the provided method string
    community_method = {
        "greedy": GreedyModularity(G, weight="weight"),
        "louvain": LouvainCommunities(G, weight="weight"),
    }.get(method)
    if community_method is None:
        raise ValueError("Unsupported community detection method")

    # Obtain the search strategy based on the provided strategy string
    strategy = {
        "fixed": FixedIncrementStrategy(),
        "dynamic": DynamicAdjustmentStrategy(
            initial_value=initial_value, adjust_factor=adjust_factor
        ),
        "adaptive": AdaptiveDynamicAdjustmentStrategy(
            target=num_languages,
            initial_value=initial_value,
            adjust_factor=adjust_factor,
        ),
    }.get(strategy_name)
    if strategy is None:
        raise ValueError("Unsupported parameter search strategy")

    history = []
    parameter = strategy.initialize()

    while True:
        identified_communities = community_method.find_communities(resolution=parameter)

        # After obtaining the communities, we must make sure that the new communities do not contradict the
        # previous ones, as the algorithm might group at this level taxa that were separated in the
        # previous one (this is a common issue in some hierarchical clustering algorithms).
        if not history:
            # First level
            communities = identified_communities
        else:
            communities = common.decompose_sets(
                history[-1].communities, identified_communities
            )

        num_communities = len(communities)

        # Store the history entry if the number of communities has increased (depending on the algorithm and the parameters,
        # the number of communities may decrease in some iterations))
        if not history or num_communities > history[-1].number_of_communities:
            history_entry = common.HistoryEntry(parameter, communities)
            history.append(history_entry)
            print(f"Parameter: {parameter:.2f}, Communities: {num_communities}")

        if strategy.should_stop(num_communities, num_languages):
            break

        parameter = strategy.update(parameter)

    return history


def remove_single_descendant_nodes(tree: TreeNode) -> TreeNode:
    """
    Removes nodes with a single descendant from an ete3 TreeNode.

    When a node with a single child is removed (a "unary" node), its child is
    connected directly to the unary node's parent (grandparent). Branch lengths
    (dist attribute) are adjusted: the child's new dist becomes the sum of its
    original dist and the dist of the removed unary node.

    If the root node itself has only one child after internal pruning, it is
    also removed, and its child becomes the new root. The new root's 'dist'
    attribute will be set to 0.

    @param tree: The root TreeNode of the tree to be pruned.
    @return: The root TreeNode of the pruned tree. This might be a different
             node if the original root was pruned.
    """

    def prune_node(node: TreeNode):
        # We use a stack to manage nodes to check (iterative depth-first)
        stack = [node]
        while stack:
            current_node = stack.pop()
            # Iterate over children list while modifying it (use a copy)
            for child_node in current_node.get_children():
                stack.append(child_node)

            # If the node has exactly one child and it's not the root
            if len(current_node.children) == 1 and current_node.up is not None:
                child = current_node.children[0]
                # Update the child's distance from its new parent (the grandparent)
                child.dist += current_node.dist

                # Connect the child directly to the grandparent
                current_node.up.add_child(child, dist=child.dist)

                # Remove the current node (which also removes it from its parent's children list)
                current_node.up.remove_child(current_node)

    # Start processing from the root
    current_root_node = tree
    prune_node(current_root_node)

    # Check if the root itself needs pruning
    if len(current_root_node.children) == 1 and not current_root_node.is_leaf():
        new_root = current_root_node.children[0]
        new_root.detach()  # Detach new_root from old_root; new_root.up becomes None.
        new_root.dist = 0.0
        current_root_node = new_root

    return current_root_node


def build_tree_from_history(history: List[common.HistoryEntry]) -> TreeNode:
    """
    Constructs a phylogenetic tree from a provided historical sequence of taxonomic groupings.

    Parameters:
    history (List[HistoryEntry]): Each HistoryEntry contains a resolution (float) and a list of frozensets.
        The resolution indicates the cumulative distance from the root of the tree,
        while each frozenset contains names of taxa that form a clade at this resolution.
        The history is expected to be sorted with resolution values increasing (from root to leaves),
        with the most granular resolution (individual taxa) last.

    Returns:
    TreeNode: The root node of the constructed ete3 phylogenetic tree.

    Notes:
    - The function assumes that the resolutions in the history are strictly increasing.
    - Polytomies (clades branching into more than two taxa) are handled naturally.
    """

    # Return an empty node if history is empty

    if not history:
        return TreeNode()

    # Initialize the root TreeNode.
    tree_root = Tree()
    node_resolutions: Dict[TreeNode, float] = {tree_root: 0.0}

    last_observed_ancestor: Dict[str, TreeNode] = {}

    # Extract all unique taxa from the most granular level of the history.
    if history[-1].communities:
        taxa = sorted(
            list(set(taxon for clade in history[-1].communities for taxon in clade))
        )
    else:
        taxa = []  # Should not happen with valid history leading to taxa

    for taxon in taxa:
        last_observed_ancestor[taxon] = tree_root

    observed_clades: List[FrozenSet[str]] = []

    # Iterate through the entire history to build the tree structure.
    for entry in history:  # Process all entries, including history[0]
        current_entry_resolution = entry.parameter
        clades_in_entry = entry.communities

        for clade_members in clades_in_entry:
            if not clade_members:  # Skip empty clades if they occur
                continue
            if clade_members in observed_clades:
                continue

            clade_label = "/".join(sorted(list(clade_members)))
            new_node = TreeNode(name=clade_label)
            node_resolutions[new_node] = current_entry_resolution

            # Determine the parent node for this new_node.
            # All members of the clade_members set should share the same last_observed_ancestor.
            potential_parents = {
                last_observed_ancestor[member]
                for member in clade_members
                if member in last_observed_ancestor
            }

            actual_parent_node: TreeNode
            if not potential_parents:
                # This implies taxa in clade_members were not in last_observed_ancestor map.
                # This could happen if history is malformed or taxa are introduced mid-history without prior record.
                # Defaulting to tree_root or raising error are options.
                # For now, we assume valid history means this path is less likely for non-root clades.
                # If current_entry_resolution is the first one, parent is tree_root.
                if current_entry_resolution == history[0].parameter:
                    actual_parent_node = tree_root
                else:
                    # This is an unexpected state for a non-root clade.
                    raise ValueError(
                        f"Clade '{clade_label}' at resolution {current_entry_resolution} has no identifiable parent. Taxa: {clade_members}"
                    )
            elif len(potential_parents) > 1:
                parent_names = sorted([p.name for p in potential_parents])
                raise ValueError(
                    f"Clade '{clade_label}' at resolution {current_entry_resolution} has multiple potential parents: "
                    f"{parent_names} ({len(potential_parents)}). This indicates inconsistent history."
                )
            else:
                actual_parent_node = potential_parents.pop()

            # Add the new node as a child of its parent. Default to 0 if parent not in map (e.g. root)
            parent_resolution = node_resolutions.get(actual_parent_node, 0.0)
            branch_length = max(1e-8, node_resolutions[new_node] - parent_resolution)
            actual_parent_node.add_child(new_node, dist=branch_length)

            observed_clades.append(clade_members)

            # Update last_observed_ancestor for all members of this new clade.
            for member in clade_members:
                last_observed_ancestor[member] = new_node

    # Post-processing: Prune unary nodes.
    final_tree_root = remove_single_descendant_nodes(tree_root)

    # Clean up internal node names and temporary features.
    for node in final_tree_root.traverse("postorder"):  # type: ignore
        if not node.is_leaf():
            node.name = ""

    final_tree_root.sort_descendants()
    final_tree_root.ladderize()

    return final_tree_root


def cognateset_graph(data: Dict[Tuple[str, str], Set[int]]) -> nx.Graph:
    """
    Builds a graph of languages with weighted edges based on shared cognate sets.

    This basic graph construction method does not take into account linguistic distances
    or the number of languages sharing the same cognate set. Each shared cognate set
    contributes equally to the weight of the edge between two languages.

    @param data: A dictionary where keys are (language, concept) pairs and values are sets of cognate set identifiers.
    @return: A graph where nodes represent languages and edges are weighted by the number of shared cognate sets
             between languages.
    """

    # Extract languages and concepts from keys
    languages = set()
    concepts = set()
    for lang, concept in data.keys():
        languages.add(lang)
        concepts.add(concept)

    # Prepare to count cognatesets shared between language pairs for each concept
    concept_lang_cognatesets = defaultdict(lambda: defaultdict(set))

    # Fill the structure with available data
    for (lang, concept), cognatesets in data.items():
        concept_lang_cognatesets[concept][lang] = cognatesets

    # Create a structure to hold weights of edges between languages
    language_pairs = defaultdict(int)

    # Calculate weights for edges by checking shared cognatesets
    for concept in concepts:
        # Get languages for this concept
        concept_languages = concept_lang_cognatesets[concept]

        # Compare each pair of languages
        lang_list = list(concept_languages.keys())
        for i in range(len(lang_list)):
            for j in range(i + 1, len(lang_list)):
                lang1 = lang_list[i]
                lang2 = lang_list[j]
                # Find intersection of cognatesets and increment weight for the pair
                shared_cognatesets = concept_lang_cognatesets[concept][
                    lang1
                ].intersection(concept_lang_cognatesets[concept][lang2])
                if shared_cognatesets:
                    language_pairs[(lang1, lang2)] += len(shared_cognatesets)
                    language_pairs[(lang2, lang1)] += len(shared_cognatesets)

    # Create the graph
    G = nx.Graph()

    # Add nodes
    for language in languages:
        G.add_node(language)

    # Add weighted edges based on shared cognatesets
    for (lang1, lang2), weight in language_pairs.items():
        if weight > 0:
            G.add_edge(lang1, lang2, weight=weight)

    return G


def adjusted_cognateset_graph(
    data: Dict[Tuple[str, str], Set[int]],
    distance_matrix: np.ndarray,
    sorted_languages: List[str],
    proximity_weight: float = 0.5,
    sharing_factor: float = 0.5,
) -> nx.Graph:
    """
    Builds a graph of languages with weighted edges based on shared cognate sets, adjusted.

    This graph construction method takes into account linguistic distances between languages
    and the number of languages sharing the same cognate set. The weight of an edge between
    two languages is adjusted based on the proximity of the languages in the distance matrix
    and the number of shared cognate sets.

    The proximity correction is calculated as 1 / (distance^proximity_weight), where distance
    is the linguistic distance between two languages. The higher the proximity_weight, the more
    the weight of the edge is adjusted based on the distance (languages that are closer in the
    distance matrix will have higher weights).

    The sharing correction is calculated as (number of shared cognate sets)^sharing_factor. The
    higher the sharing_factor, the more the weight of the edge is adjusted based on the number of
    shared cognate sets (languages that share more cognate sets will have higher weights).

    @param data: A dictionary where keys are (language, concept) pairs and values are sets of cognate set identifiers.
    @param distance_matrix: A 2D numpy array representing the linguistic distance between languages.
    @param sorted_languages: A list of languages in the order they appear in the distance matrix.
    @param proximity_weight: A float representing the weight of proximity in the adjustment calculation.
    @param sharing_factor: A float representing the weight of sharing in the adjustment calculation.
    @return: A graph where nodes represent languages and edges are weighted by the number of shared cognate sets
             between languages, adjusted by linguistic distance and sharing factors.
    """
    language_index = {lang: idx for idx, lang in enumerate(sorted_languages)}

    languages = set()
    concepts = set()
    for lang, concept in data.keys():
        languages.add(lang)
        concepts.add(concept)

    concept_lang_cognatesets = defaultdict(lambda: defaultdict(set))
    for (lang, concept), cognatesets in data.items():
        concept_lang_cognatesets[concept][lang] = cognatesets

    language_pairs = defaultdict(float)

    # Calculate weights for edges by checking shared cognatesets
    for concept, langs in concept_lang_cognatesets.items():
        lang_list = list(langs.keys())
        num_langs = len(lang_list)
        for i in range(num_langs):
            for j in range(i + 1, num_langs):
                lang1, lang2 = lang_list[i], lang_list[j]
                if lang1 in language_index and lang2 in language_index:
                    shared_cognatesets = langs[lang1].intersection(langs[lang2])
                    if shared_cognatesets:
                        idx1, idx2 = language_index[lang1], language_index[lang2]
                        proximity_correction = 1 / (
                            distance_matrix[idx1, idx2] ** proximity_weight
                        )
                        sharing_correction = len(shared_cognatesets) ** sharing_factor
                        weight_adjustment = proximity_correction * sharing_correction
                        language_pairs[(lang1, lang2)] += weight_adjustment
                        language_pairs[(lang2, lang1)] += weight_adjustment

    # Create the graph
    G = nx.Graph()
    for language in languages:
        G.add_node(language)
    for (lang1, lang2), weight in language_pairs.items():
        if weight > 0:
            G.add_edge(lang1, lang2, weight=weight)

    return G


def build_graph(method: str, **kwargs) -> nx.Graph:
    """
    Selects and executes a graph construction method based on the provided method string.

    @param method: A string indicating the graph construction method to use.
    @param kwargs: Additional keyword arguments to pass to the selected graph construction method.
    @return: A graph constructed using the selected method.
    """
    graph_methods = {
        "cognateset_graph": cognateset_graph,
        "adjusted_cognateset_graph": adjusted_cognateset_graph,
    }
    if method in graph_methods:
        return graph_methods[method](**kwargs)
    else:
        raise ValueError(f"Invalid graph construction method: {method}")


def main(args):
    # Read the cognate data from a file
    cognates = common.read_cognate_file(
        args["source"],
        args["dialect"],
        args["encoding"],
        args["language_column"],
        args["concept_column"],
        args["cognateset_column"],
    )

    # Obtain a sorted list of languages and concepts, and then their counts
    languages = sorted({lang for lang, _ in cognates.keys()})
    concepts = sorted({concept for _, concept in cognates.keys()})
    num_languages = len(languages)

    # Build the graph
    G = None
    if args["graph"] == "unadjusted":
        G = build_graph("cognateset_graph", data=cognates)
    elif args["graph"] == "adjusted":
        # Compute the distance matrix
        distance_matrix = common.compute_distance_matrix(
            cognates, synonyms=args["synonyms"], missing_data=args["missing_data"]
        )

        G = build_graph(
            "adjusted_cognateset_graph",
            data=cognates,
            distance_matrix=distance_matrix,
            sorted_languages=languages,
            proximity_weight=args["proximity_weight"],
            sharing_factor=args["sharing_factor"],
        )
    if G is None:
        raise ValueError("Graph could not be built. Please check the --graph argument.")

    # Write a visualization of the graph to a file
    # nx.write_gexf(G, "graph.gexf")
    logging.info("Graph built successfully.")

    family_history = build_history(
        G,
        num_languages,
        method=args["community"],
        strategy_name=args["strategy"],
        initial_value=args["initial_value"],
        adjust_factor=args["adjust_factor"],
    )

    phylogeny = build_tree_from_history(family_history)
    logging.info(f"Phylogeny: {phylogeny}")

    # Print the tree in Newick format, with internal node names and branch lengths
    newick_tree = phylogeny.write(format=1)
    logging.info(f"Newick format tree: {newick_tree}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform phylogenetic reconstruction using GRAPE."
    )

    # Define the arguments with argparse
    parser.add_argument(
        "source",
        help="Source file name (must be a cognateset file, three columns separated by tabs)",
    )
    parser.add_argument(
        "--dialect",
        default="auto",
        help="CSV dialect to use. Examples: 'excel', 'excel-tab', 'unix'. "
        "If 'auto', the script will try to detect it. "
        f"All available system dialects: {csv.list_dialects()}",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding of the input file (e.g., 'utf-8', 'latin-1'). Default: 'utf-8'.",
    )
    parser.add_argument(
        "--language-column",
        default="Language",
        help="Name of the column containing language identifiers. Default: 'Language'.",
    )
    parser.add_argument(
        "--concept-column",
        default="Parameter",
        help="Name of the column containing concept/parameter identifiers. Default: 'Parameter'.",
    )
    parser.add_argument(
        "--cognateset-column",
        default="Cognateset",
        help="Name of the column containing cognateset identifiers. Default: 'Cognateset'.",
    )
    parser.add_argument(
        "--graph",
        default="adjusted",
        choices=[
            "adjusted",
            "unadjusted",
        ],
        help="Method to create the graph",
    )
    parser.add_argument(
        "--community",
        default="louvain",
        choices=["greedy", "louvain"],
        help="Method to detect communities",
    )
    parser.add_argument(
        "--strategy",
        default="fixed",
        choices=["fixed", "dynamic", "adaptive"],
        help="Strategy to use",
    )
    parser.add_argument(
        "--synonyms",
        default="average",
        choices=["average", "min", "max"],
        help="Strategy to handle synonyms when using adjusted weights",
    )
    parser.add_argument(
        "--missing_data",
        "-m",
        default="max_dist",
        choices=["max_dist", "zero", "ignore"],
        help="Strategy to handle missing data when using adjusted weights",
    )
    parser.add_argument(
        "--initial_value",
        type=float,
        default=0.0,
        help="Initial value if strategy is dynamic or adaptive",
    )
    parser.add_argument(
        "--adjust_factor",
        type=float,
        default=0.1,
        help="Adjust factor if strategy is dynamic or adaptive",
    )
    parser.add_argument(
        "--proximity_weight",
        "-p",
        type=float,
        default=0.5,
        help="Weight for the proximity correction when using adjusted weights",
    )
    parser.add_argument(
        "--sharing_factor",
        "-s",
        type=float,
        default=0.5,
        help="Factor for the sharing correction when using adjusted weights",
    )

    # Parse arguments
    args = parser.parse_args()

    # Pass the parsed arguments to the main function
    main(vars(args))
