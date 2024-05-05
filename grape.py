import networkx as nx

from dataclasses import dataclass
from typing import List, FrozenSet, Dict, Set, Tuple
from functools import cached_property

import phylodata
import graph


@dataclass
class HistoryEntry:
    """Class to store a history entry with resolution and communities.

    Attributes:
        resolution (float): The resolution value indicating the distance to the root.
        communities (List[FrozenSet[str]]): A list of communities, each represented as a frozenset of strings.
    """

    resolution: float
    communities: List[FrozenSet[str]]

    @cached_property
    def number_of_communities(self) -> int:
        """Returns the number of communities in this history entry, caching the result."""
        return len(self.communities)


# TODO: Work on dynamic resolution adjustment


def build_history(G, num_languages):
    # Iterate with different resolutions
    resolution = 0.0
    history = []
    while True:
        resolution += 0.1

        community_generator = nx.algorithms.community.greedy_modularity_communities(
            G, weight="weight", resolution=resolution
        )
        communities = [frozenset(community) for community in community_generator]
        num_communities = len(communities)

        # If `history` is empty or the number of communities is different from the last entry
        if not history or num_communities != history[-1].number_of_communities:
            history_entry = HistoryEntry(resolution, communities)
            history.append(history_entry)
            print(f"Resolution: {resolution:.1f}, Communities: {num_communities}")
            print(communities)

        if num_communities == num_languages:
            break

    return history


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
        resolution, clades = entry.resolution, entry.communities
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


import matplotlib.pyplot as plt


def draw_and_save_graph(G):
    plt.figure(figsize=(8, 6))  # Set the size of the image
    nx.draw(
        G,
        with_labels=True,
        node_color="skyblue",
        font_weight="bold",
        node_size=700,
        font_size=9,
    )
    plt.title("Language Graph")
    plt.savefig("language_graph.png")  # Save the graph to a file
    plt.close()  # Close the plot to free up memory


def main():
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

    # G = graph.build_language_graph(cognates)
    G = graph.build_language_graph2(cognates, distance_matrix, languages)
    print(G.edges(data=True))

    history = build_history(G, num_languages)
    print(len(history))

    tree = build_tree_from_history(history)
    print(tree)

    # Print the tree in Newick format, with internal node names and branch lengths
    print(tree.write(format=1))


if __name__ == "__main__":
    main()
