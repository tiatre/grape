#!/usr/bin/env python

# TODO: make sure it works with any cognateid type, ints, strings, etc.
# TODO: use logging instead of print

# Import libraries
from typing import Dict, Set, Tuple
import argparse
import csv
import numpy as np

# Import local modules
import graph
import history
import tree


def read_cognate_file(
    input_file: str, dialect_name: str, encoding: str
) -> Dict[Tuple[str, str], Set[int]]:
    """
    Reads a cognateset file, returning a dictionary mapping (language, concept) pairs to sets of cognatesets.

    The file is expected to contain three fields: language, concept, and cognate set identifier.
    The cognate set identifier is expected to be in the format "id.number", where "number" is parsed as an integer.

    @param input_file: The path to the cognateset file.
    @param dialect_name: The CSV dialect to use. If "auto", it will be sniffed.
                         Examples: 'excel', 'excel-tab', 'unix'.
    @param encoding: The encoding of the input file (e.g., 'utf-8', 'latin-1').
    @return: A dictionary where keys are tuples of (language, concept) and values are sets of cognatesets.
    """
    cognates_dict = {}

    try:
        with open(input_file, "r", encoding=encoding, newline="") as f_in:
            actual_dialect_for_reader = None

            if dialect_name == "auto":
                # Read a sample for sniffing, then reset position
                sample = f_in.read(2048)
                f_in.seek(0)

                if not sample.strip():  # Check if sample is empty or whitespace only
                    print(
                        f"Warning: File '{input_file}' is empty or sample is insufficient for dialect sniffing. Falling back to 'excel-tab'."
                    )
                    actual_dialect_for_reader = "excel-tab"
                else:
                    sniffer = csv.Sniffer()
                    try:
                        dialect_from_sample = sniffer.sniff(sample)
                        # Ensure lineterminator is representable for printing
                        lineterminator_repr = repr(dialect_from_sample.lineterminator)
                        print(
                            f"Detected CSV dialect: Delimiter='{dialect_from_sample.delimiter}', Quotechar='{dialect_from_sample.quotechar}', Lineterminator={lineterminator_repr}"
                        )
                        actual_dialect_for_reader = dialect_from_sample
                    except csv.Error as e:
                        print(
                            f"Could not automatically detect CSV dialect from sample: {e}. Falling back to 'excel-tab'."
                        )
                        actual_dialect_for_reader = "excel-tab"
            else:
                if dialect_name not in csv.list_dialects():
                    available_dialects = ", ".join(csv.list_dialects())
                    raise ValueError(
                        f"Unknown CSV dialect: '{dialect_name}'. "
                        f"Available dialects: {available_dialects}. "
                        "Or use 'auto' for detection."
                    )
                actual_dialect_for_reader = dialect_name

            # Use the determined dialect with csv.reader
            reader = csv.reader(f_in, actual_dialect_for_reader)

            # Skip the header line
            try:
                next(reader)
            except StopIteration:
                # This means the file (after potential BOM and dialect sniffing) was empty or header-only
                print(
                    f"Warning: CSV file '{input_file}' is empty or contains only a header. No data to read."
                )
                return cognates_dict

            # Read the data, starting from the second line (first line is header)
            for row_number, parts in enumerate(reader, start=2):
                if len(parts) != 3:
                    raise ValueError(
                        f"Line {row_number} in '{input_file}': Expected 3 fields, but found {len(parts)}. Row content: {parts}"
                    )

                lang, concept, cognateset_str = parts

                # Skip if cognateset is empty
                if not cognateset_str:
                    continue

                try:
                    cognateset_val = int(cognateset_str.split(".")[1])
                except IndexError:
                    raise ValueError(
                        f"Line {row_number} in '{input_file}': Cognateset identifier '{cognateset_str}' must be in the format 'id.number'"
                    )
                except ValueError:
                    raise ValueError(
                        f"Line {row_number} in '{input_file}': The second part of the cognateset identifier '{cognateset_str}' must be an integer."
                    )

                # Create a key as a tuple of language and concept
                key = (lang, concept)

                # Add cognateset to the set for the corresponding language-concept pair
                if key not in cognates_dict:
                    cognates_dict[key] = set()
                cognates_dict[key].add(cognateset_val)

    except FileNotFoundError:
        raise FileNotFoundError(f"The file {input_file} does not exist.")
    except UnicodeDecodeError as e:
        raise ValueError(
            f"Could not decode file {input_file} with encoding '{encoding}'. Please specify the correct encoding using --encoding. Original error: {e}"
        ) from e
    except csv.Error as e:
        raise ValueError(f"CSV processing error in file '{input_file}': {e}") from e

    return cognates_dict


# TODO: add strategy and missing data to command line parameters
def compute_distance_matrix(
    cognates: Dict[Tuple[str, str], Set[int]],
    strategy: str = "average",
    missing_data: str = "max_dist",
) -> np.ndarray:
    """
    Computes a pairwise distance matrix for languages based on their cognate sets.

    @param cognates: A dictionary where keys are tuples of (language, concept) and values are sets of cognatesets.
    @param strategy: The strategy for handling synonyms ("average", "min", "max").
    @param missing_data: The strategy for handling missing data ("max_dist", "zero", "ignore").
    @return: A symmetric matrix of distances between each pair of languages.
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
    cognates = read_cognate_file(args["source"], args["dialect"], args["encoding"])

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
    if G is None:
        raise ValueError("Graph could not be built. Please check the --graph argument.")

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
