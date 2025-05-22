#!/usr/bin/env python

# Import libraries
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import argparse
import csv
import logging  
import networkx as nx
import numpy as np

# Import local modules
import common
import history
import tree

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

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

    family_history = history.build_history(
        G,
        num_languages,
        method=args["community"],
        strategy_name=args["strategy"],
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
