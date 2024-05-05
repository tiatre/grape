from typing import List, FrozenSet, Dict, Set, Tuple
import numpy as np
import networkx as nx
from collections import defaultdict


def build_language_graph(data):
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


def build_language_graph2(
    data: Dict[Tuple[str, str], Set[int]],
    distance_matrix: np.ndarray,
    sorted_languages: List[str],
    proximity_weight: float = 0.5,
    sharing_factor: float = 0.5,
) -> nx.Graph:
    """
    Builds a graph of languages with weighted edges based on shared cognate sets,
    adjusted for the linguistic distance and the number of sharing languages.

    Args:
        data (Dict[Tuple[str, str], Set[int]]): A dictionary where keys are (language, concept)
            pairs and values are sets of cognateset identifiers.
        distance_matrix (np.ndarray): A 2D numpy array with pairwise linguistic distances between languages.
        sorted_languages (List[str]): A list of language names corresponding to the indices in the distance_matrix.
        proximity_weight (float): A factor to adjust the significance of cognate sharing based on linguistic proximity.
        sharing_factor (float): A factor to increase weight if more languages share the same cognateset.

    Returns:
        nx.Graph: A graph where nodes represent languages and edges are weighted by the adjusted
                  significance of shared cognatesets.
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

    G = nx.Graph()
    for language in languages:
        G.add_node(language)
    for (lang1, lang2), weight in language_pairs.items():
        if weight > 0:
            G.add_edge(lang1, lang2, weight=weight)

    return G
