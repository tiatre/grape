import argparse

import networkx as nx


from typing import List, FrozenSet, Dict, Set, Tuple


import phylodata
import graph
import history
import tree


def main(args):
    # Read the cognate data from a file
    cognates = phylodata.read_cognate_file(args["source"])

    # Obtain a sorted list of languages and concepts, and then their counts
    languages = sorted({lang for lang, _ in cognates.keys()})
    concepts = sorted({concept for _, concept in cognates.keys()})
    num_languages = len(languages)
    num_concepts = len(concepts)

    # Compute the distance matrix
    distance_matrix = phylodata.compute_distance_matrix(cognates)

    # Build the graph
    if args["graph"] == "cognateset_graph":
        G = graph.build_graph("cognateset_graph", data=cognates)
    elif args["graph"] == "adjusted_cognateset_graph":
        G = graph.build_graph(
            "adjusted_cognateset_graph",
            data=cognates,
            distance_matrix=distance_matrix,
            sorted_languages=languages,
        )

    # Write a visualization of the graph to a file
    # nx.write_gexf(G, "graph.gexf")

    family_history = history.build_history(G, num_languages, method=args["community"])

    phylogeny = tree.build_tree_from_history(family_history)
    print(phylogeny)

    # Print the tree in Newick format, with internal node names and branch lengths
    print(phylogeny.write(format=1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some parameters.")

    # Define the arguments with argparse
    parser.add_argument("source", help="Source file name")
    parser.add_argument(
        "--graph",
        default="cognateset_graph",
        choices=["adjusted_cognateset_graph", "cognateset_graph"],
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
        default="adaptive",
        choices=["fixed", "dynamic", "adaptive"],
        help="Strategy to use",
    )
    parser.add_argument(
        "--initial_value",
        type=float,
        help="Initial value if strategy is dynamic or adaptive",
    )
    parser.add_argument(
        "--adjust_factor",
        type=float,
        help="Adjust factor if strategy is dynamic or adaptive",
    )

    # Parse arguments
    args = parser.parse_args()

    # Pass the parsed arguments to the main function
    main(vars(args))
