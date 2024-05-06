import networkx as nx


from typing import List, FrozenSet, Dict, Set, Tuple
from common import HistoryEntry

import phylodata
import graph
import history


from ete3 import Tree, TreeNode


def build_tree_from_history(history: List[HistoryEntry]):
    """
    Constructs a phylogenetic tree from a provided historical sequence of taxonomic groupings.

    Parameters:
    history (List[HistoryEntry]): Each HistoryEntry contains a resolution (float) and a list of frozensets.
        The resolution indicates the cumulative distance from the root of the tree,
        while each frozenset contains names of taxa that form a clade at this resolution.
        The history is expected to be sorted from the most distant from the root to the closest,
        with the most granular resolution (individual taxa) last.

    Returns:
    Tree: An ete3 Tree object representing the constructed phylogenetic tree.

    Notes:
    - The function assumes that the resolutions in the history are strictly increasing as the
      history progresses from the start (root) to the end (leaves).
    - Polytomies (clades branching into more than two taxa) are handled naturally by this approach.
    """

    # Initialize an empty ete3 Tree object.
    tree = Tree()
    last_observed_ancestor = {}

    # Extract all taxa from the last element in history, which contains the most granular clades (individual taxa).
    taxa = sorted(taxon for clade in history[-1].communities for taxon in clade)

    # Initialize the last observed ancestor of each taxon to the root of the tree.
    for taxon in taxa:
        last_observed_ancestor[taxon] = tree

    # Iterate through the history, starting from the second entry to avoid redundancy with the root initialization.
    observed_clades = {}
    for entry in history[1:]:
        resolution, clades = entry.parameter, entry.communities
        for clade in clades:
            # Create a label for the clade using sorted taxa names to ensure uniqueness and consistency.
            clade_label = ",".join(sorted(clade))

            # Avoid processing the same clade label more than once.
            if clade_label in observed_clades:
                if len(clade) > 1:
                    observed_clades[clade_label].dist = resolution
                continue

            # Create a new node for the clade.
            node = TreeNode(name=clade_label if len(clade) == 1 else "")

            # Connect the new clade node to its ancestor nodes, ensuring no duplicate branches are created.
            branches_added = set()
            for taxon in clade:
                ancestor = last_observed_ancestor[taxon]
                if ancestor not in branches_added:
                    if ancestor == tree:
                        branch_length = resolution
                    else:
                        branch_length = max(1e-8, resolution - ancestor.dist)
                    ancestor.add_child(node, dist=branch_length)
                    branches_added.add(ancestor)

                # Update the last observed ancestor for each taxon to the current clade's node.
                last_observed_ancestor[taxon] = node

            # Record this clade label to prevent future reprocessing.
            observed_clades[clade_label] = node

    return tree


def main(args):
    # Read the cognate data from a file
    cognates = phylodata.read_cognate_file("ie.tsv")

    # Obtain a sorted list of languages and concepts, and then their counts
    languages = sorted({lang for lang, _ in cognates.keys()})
    concepts = sorted({concept for _, concept in cognates.keys()})
    num_languages = len(languages)
    num_concepts = len(concepts)

    # Compute the distance matrix
    distance_matrix = phylodata.compute_distance_matrix(cognates)
    print(distance_matrix)

    # Build the graph
    if args["graph_method"] == "cognateset_graph":
        G = graph.build_graph("cognateset_graph", data=cognates)
    elif args["graph_method"] == "adjusted_cognateset_graph":
        G = graph.build_graph(
            "adjusted_cognateset_graph",
            data=cognates,
            distance_matrix=distance_matrix,
            sorted_languages=languages,
        )

    # print(G.edges(data=True))

    family_history = history.build_history(
        G, num_languages, method=args["community_method"]
    )
    print(len(family_history))

    tree = build_tree_from_history(family_history)
    print(tree)

    # Print the tree in Newick format, with internal node names and branch lengths
    print(tree.write(format=1))


if __name__ == "__main__":
    args = {
        "graph_method": "adjusted_cognateset_graph",  # or "cognateset_graph"
        "input_file": "ie.tsv",
        "community_method": "louvain_communities",  # or "greedy"
    }
    main(args)
