#!/usr/bin/env python

# Import standard libraries
import argparse
from typing import Dict, Set, Tuple

# Import third-party libraries
import numpy as np

# Import local modules
import graph
import history
import tree


def read_cognate_file(input_file: str) -> Dict[Tuple[str, str], Set[int]]:
    """
    Reads a cognateset file, returning a dictionary mapping (language, concept) pairs to sets of cognatesets.

    The file is expected to have a tab-separated format with a header. Each line after the header
    should contain three fields: language, concept, and cognate set identifier. The cognate set
    identifier is expected to be in the format "id.number", where "number" is parsed as an integer.

    Args:
        input_file (str): The path to the input file.

    Returns:
        Dict[Tuple[str, str], Set[int]]: A dictionary where keys are tuples of (language, concept)
        and values are sets of integers representing cognate set identifiers.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If any line in the file does not have exactly three tab-separated values or if the
                    cognate set identifier format is incorrect.
    """
    cognates_dict = {}

    try:
        with open(input_file, "r", encoding="utf-8") as f_in:
            # Skip the header line
            next(f_in)

            for line in f_in:
                # Split the line by tabs and ensure it contains exactly three parts
                parts = line.strip().split("\t")
                if len(parts) != 3:
                    raise ValueError(
                        f"Each line must contain exactly three tab-separated fields (line `{line}`)."
                    )

                lang, concept, cognateset = parts

                # Skip if cognateset is empty
                if not cognateset:
                    continue

                try:
                    # Extract the integer part of the cognateset identifier
                    cognateset = int(cognateset.split(".")[1])
                except IndexError:
                    raise ValueError(
                        "Cognateset identifier must be in the format 'id.number'"
                    )
                except ValueError:
                    raise ValueError(
                        "The second part of the cognateset identifier must be an integer."
                    )

                # Create a key as a tuple of language and concept
                key = (lang, concept)

                # Add cognateset to the set for the corresponding language-concept pair
                if key not in cognates_dict:
                    cognates_dict[key] = set()
                cognates_dict[key].add(cognateset)

    except FileNotFoundError:
        raise FileNotFoundError(f"The file {input_file} does not exist")

    return cognates_dict


# TODO: add strategy and missing data to command line parameters
def compute_distance_matrix(
    cognates: Dict[Tuple[str, str], Set[int]],
    strategy: str = "average",
    missing_data: str = "max_dist",
) -> np.ndarray:
    """
    Computes a pairwise distance matrix for languages based on their cognate sets.

    Args:
        cognates (Dict[Tuple[str, str], Set[int]]): The dictionary of cognate data.
        strategy (str): The strategy for handling synonyms ("average", "min", "max").
        missing_data (str): The strategy for handling missing data ("max_dist", "zero", "ignore").

    Returns:
        np.ndarray: A symmetric matrix of distances between each pair of languages.
    """
    # Extract unique languages and concepts
    languages = sorted({lang for lang, _ in cognates.keys()})
    concepts = sorted({concept for _, concept in cognates.keys()})

    # Initialize the distance matrix
    dist_matrix = np.zeros((len(languages), len(languages)))

    # Helper function to calculate distance between sets of cognates
    def _calculate_distance(set1: Set[int], set2: Set[int]) -> float:
        if not set1 or not set2:
            return 0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return 1 - len(intersection) / len(union)

    # Compute pairwise distances
    for i, lang1 in enumerate(languages):
        for j, lang2 in enumerate(languages):
            if j <= i:
                continue  # This matrix is symmetric, so skip redundant calculations

            distances = []
            for concept in concepts:
                cognates1 = cognates.get((lang1, concept), set())
                cognates2 = cognates.get((lang2, concept), set())

                if not cognates1 and not cognates2:
                    if missing_data == "max_dist":
                        distances.append(1)
                    elif missing_data == "zero":
                        distances.append(0)
                else:
                    if strategy == "min":
                        min_dist = min(
                            [
                                _calculate_distance({c1}, {c2})
                                for c1 in cognates1
                                for c2 in cognates2
                            ],
                            default=1,
                        )
                        distances.append(min_dist)
                    elif strategy == "max":
                        max_dist = max(
                            [
                                _calculate_distance({c1}, {c2})
                                for c1 in cognates1
                                for c2 in cognates2
                            ],
                            default=1,
                        )
                        distances.append(max_dist)
                    elif strategy == "average":
                        all_dists = [
                            _calculate_distance({c1}, {c2})
                            for c1 in cognates1
                            for c2 in cognates2
                        ]
                        if all_dists:
                            avg_dist = sum(all_dists) / len(all_dists)
                        else:
                            avg_dist = 1
                        distances.append(avg_dist)

            # Compute and assign the average distance for this language pair
            if distances:
                dist = sum(distances) / len(distances)
            else:
                dist = 1
            dist_matrix[i, j] = dist_matrix[j, i] = dist

    return dist_matrix


def main(args):
    # Read the cognate data from a file
    cognates = read_cognate_file(args["source"])

    # Obtain a sorted list of languages and concepts, and then their counts
    languages = sorted({lang for lang, _ in cognates.keys()})
    concepts = sorted({concept for _, concept in cognates.keys()})
    num_languages = len(languages)
    num_concepts = len(concepts)

    # Build the graph
    if args["graph"] == "cognateset_graph":
        G = graph.build_graph("cognateset_graph", data=cognates)
    elif args["graph"] == "adjusted_cognateset_graph":
        # Compute the distance matrix
        distance_matrix = compute_distance_matrix(
            cognates, missing_data=args["missing_data"]
        )

        G = graph.build_graph(
            "adjusted_cognateset_graph",
            data=cognates,
            distance_matrix=distance_matrix,
            sorted_languages=languages,
            proximity_weight=args["proximity_weight"],
            sharing_factor=args["sharing_factor"],
        )

    # Write a visualization of the graph to a file
    # nx.write_gexf(G, "graph.gexf")

    family_history = history.build_history(
        G,
        num_languages,
        method=args["community"],
        strategy=args["strategy"],
        initial_value=args["initial_value"],
        adjust_factor=args["adjust_factor"],
    )

    phylogeny = tree.build_tree_from_history(family_history)
    print(phylogeny)

    # Print the tree in Newick format, with internal node names and branch lengths
    print(phylogeny.write(format=1))


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
        "--graph",
        default="adjusted_cognateset_graph",
        choices=[
            "adjusted_cognateset_graph",
            "cognateset_graph",
        ],  # TODO: remname to "adjusted" and "unadjusted"
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
