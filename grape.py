import networkx as nx


from typing import List, FrozenSet, Dict, Set, Tuple


import phylodata
import graph
import history
import tree


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

    phylogeny = tree.build_tree_from_history(family_history)
    print(phylogeny)

    # Print the tree in Newick format, with internal node names and branch lengths
    print(phylogeny.write(format=1))


if __name__ == "__main__":
    args = {
        "graph_method": "adjusted_cognateset_graph",  # or "cognateset_graph"
        "input_file": "ie.tsv",
        "community_method": "louvain_communities",  # or "greedy"
    }
    main(args)
