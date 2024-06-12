# Import standard libraries
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Import third-party libraries
import networkx as nx
import numpy as np


def cognateset_graph(data: Dict[Tuple[str, str], Set[int]]) -> nx.Graph:
    """
    Builds a graph of languages with weighted edges based on shared cognate sets.

    This basic graph construction method does not take into account linguistic distances
    or the number of languages sharing the same cognate set. Each shared cognate set
    contributes equally to the weight of the edge between two languages.

    Args:
        data (Dict[Tuple[str, str], Set[int]]): A dictionary where keys are (language, concept)
            pairs and values are sets of cognate set identifiers.

    Returns:
        nx.Graph: A graph where nodes represent languages and edges are weighted by the number
                  of shared cognate sets between languages.
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

    Args:
        data (Dict[Tuple[str, str], Set[int]]): A dictionary where keys are (language, concept)
            pairs and values are sets of cognate set identifiers.
        distance_matrix (np.ndarray): A symmetric matrix of distances between languages.
        sorted_languages (List[str]): A list of languages sorted in the same order as the distance matrix.
        proximity_weight (float): A weight factor for the proximity correction (default: 0.5).
        sharing_factor (float): A factor for the number of shared cognate sets correction (default: 0.5).

    Returns:
        nx.Graph: A graph where nodes represent languages and edges are weighted by the adjusted
                  number of shared cognate sets between languages.
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

    Args:
        method (str): Name of the method to execute. Can be 'cognateset_graph' or 'adjusted_cognateset_graph'.
        kwargs: Arguments required by the selected graph construction method.

    Returns:
        nx.Graph: The resulting graph from the selected method.

    Raises:
        ValueError: If an invalid method name is provided.
    """
    graph_methods = {
        "cognateset_graph": cognateset_graph,
        "adjusted_cognateset_graph": adjusted_cognateset_graph,
    }
    if method in graph_methods:
        return graph_methods[method](**kwargs)
    else:
        raise ValueError(f"Invalid graph construction method: {method}")
