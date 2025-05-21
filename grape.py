#!/usr/bin/env python

# Import libraries
import argparse
import csv
import logging  

# Import local modules
import common
import graph
import history
import tree

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


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
        G = graph.build_graph("cognateset_graph", data=cognates)
    elif args["graph"] == "adjusted":
        # Compute the distance matrix
        distance_matrix = common.compute_distance_matrix(
            cognates, synonyms=args["synonyms"], missing_data=args["missing_data"]
        )

        G = graph.build_graph(
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

    family_history = history.build_history(
        G,
        num_languages,
        method=args["community"],
        strategy=args["strategy"],
        initial_value=args["initial_value"],
        adjust_factor=args["adjust_factor"],
    )

    phylogeny = tree.build_tree_from_history(family_history)
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
