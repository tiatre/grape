from dataclasses import dataclass
from functools import cached_property
from typing import List, FrozenSet, Dict, Set, Tuple
import csv
import logging
import numpy as np


@dataclass
class HistoryEntry:
    """Class to store a history entry with resolution and communities.

    Attributes:
        parameter (float): The resolution value indicating the distance to the root.
        communities (List[FrozenSet[str]]): A list of communities, each represented as a frozenset of strings.
    """

    parameter: float
    communities: List[FrozenSet[str]]

    @cached_property
    def number_of_communities(self) -> int:
        """Returns the number of communities in this history entry, caching the result."""
        return len(self.communities)


def read_cognate_file(
    input_file: str,
    dialect_name: str,
    encoding: str,
    lang_col_name: str,
    concept_col_name: str,
    cognateset_col_name: str,
) -> Dict[Tuple[str, str], Set[int]]:
    """
    Reads a cognateset file, returning a dictionary mapping (language, concept) pairs to sets of cognatesets.

    The file is expected to contain columns for language, concept/parameter, and cognateset identifiers.
    The names of these columns can be specified. Defaults are "Language", "Parameter", and "Cognateset".
    The cognate set identifier in the cognateset column is expected to be in the format "id.number",
    where "number" is parsed as an integer.

    @param input_file: The path to the cognateset file.
    @param dialect_name: The CSV dialect to use. If "auto", it will be sniffed.
    @param encoding: The encoding of the input file.
    @param lang_col_name: The name of the column containing language identifiers.
    @param concept_col_name: The name of the column containing concept/parameter identifiers.
    @param cognateset_col_name: The name of the column containing cognateset identifiers.
    @return: A dictionary where keys are tuples of (language, concept) and values are sets of cognatesets.
    """
    cognates_dict = {}
    cognateset_string_to_id_map: Dict[Tuple[str, str], int] = {}
    next_cognateset_id: int = 1

    required_columns = [lang_col_name, concept_col_name, cognateset_col_name]

    try:
        with open(input_file, "r", encoding=encoding, newline="") as f_in:
            actual_dialect_for_reader = None

            if dialect_name == "auto":
                # Read a sample for sniffing, then reset position
                sample = f_in.read(2048)
                f_in.seek(0)

                if not sample.strip():  # Check if sample is empty or whitespace only
                    logging.warning(  # Replace print with logging
                        f"File '{input_file}' is empty or sample is insufficient for dialect sniffing. Falling back to 'excel-tab'."
                    )
                    actual_dialect_for_reader = "excel-tab"
                else:
                    sniffer = csv.Sniffer()
                    try:
                        dialect_from_sample = sniffer.sniff(sample)
                        # Ensure lineterminator is representable for printing
                        lineterminator_repr = repr(dialect_from_sample.lineterminator)
                        logging.info(  # Replace print with logging
                            f"Detected CSV dialect: Delimiter='{dialect_from_sample.delimiter}', Quotechar='{dialect_from_sample.quotechar}', Lineterminator={lineterminator_repr}"
                        )
                        actual_dialect_for_reader = dialect_from_sample
                    except csv.Error as e:
                        logging.warning(  # Replace print with logging
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

            reader = csv.DictReader(f_in, dialect=actual_dialect_for_reader)

            if reader.fieldnames is None:
                raise ValueError(
                    f"Could not read header from CSV file '{input_file}'. The file might be empty or improperly formatted."
                )

            # Check for required column headers (case-sensitive)
            missing_columns = [
                col for col in required_columns if col not in reader.fieldnames
            ]
            if missing_columns:
                raise ValueError(
                    f"Missing required columns in '{input_file}': {missing_columns}. "
                    f"Please check column names or use command-line options to specify them. "
                    f"Found columns: {reader.fieldnames}"
                )

            for row_number, row_dict in enumerate(reader, start=2):
                lang = row_dict.get(lang_col_name)
                concept = row_dict.get(concept_col_name)
                cognateset_str = row_dict.get(cognateset_col_name)

                # Check for empty values in required columns (including cognateset_str)
                if not lang or not concept or not cognateset_str:
                    logging.warning(  # Replace print with logging
                        f"Line {row_number} in '{input_file}': Skipping row due to missing value(s) "
                        f"for columns '{lang_col_name}', '{concept_col_name}', or '{cognateset_col_name}'. Data: {row_dict}"
                    )
                    continue

                # Get or create integer ID for the (concept, cognateset_string) pair
                cognateset_map_key = (
                    concept,
                    cognateset_str,
                )  # concept is definitely not None here
                if cognateset_map_key not in cognateset_string_to_id_map:
                    cognateset_string_to_id_map[cognateset_map_key] = next_cognateset_id
                    next_cognateset_id += 1

                cognateset_val = cognateset_string_to_id_map[cognateset_map_key]

                key = (lang, concept)
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


def compute_distance_matrix(
    cognates: Dict[Tuple[str, str], Set[int]],
    synonyms: str = "average",
    missing_data: str = "max_dist",
) -> np.ndarray:
    """
    Computes a pairwise distance matrix for languages based on their cognate sets.

    The distance between two languages is the average of the distances for each concept.
    If no concepts can be compared (e.g., due to missing data and "ignore" strategy),
    the overall distance is 1.

    @param cognates: A dictionary where keys are tuples of (language, concept)
                     and values are sets of cognateset IDs (integers).
    @param synonyms: The strategy for handling synonyms (multiple cognates for the
                     same concept in a language).
                     - "average": The distance for a concept is the average of
                       pairwise Jaccard distances between all cognates of lang1
                       and all cognates of lang2 for that concept.
                     - "min": The distance for a concept is the minimum of these
                       pairwise Jaccard distances. Results in 0 if there's any
                       shared cognate ID, 1 otherwise.
                     - "max": The distance for a concept is the maximum of these
                       pairwise Jaccard distances. Results in 1 if cognate sets
                       are not identical (even if they are subsets or if multiple
                       synonyms exist, e.g. L1={A,B}, L2={A,B} -> dist=1 for concept),
                       0 only if both languages have the exact same single cognate ID.
    @param missing_data: The strategy for handling missing data for a concept.
                     - "max_dist": If both languages lack cognates for a concept,
                       a distance of 1 is assigned for that concept.
                     - "zero": If both languages lack cognates for a concept,
                       a distance of 0 is assigned for that concept.
                     - "ignore": If both languages lack cognates for a concept,
                       that concept is ignored (does not contribute to the
                       average distance).
                     Note: If one language has cognates for a concept and the
                     other does not, the concept contributes a distance of 1 to the
                     language pair's list of concept distances, regardless of this
                     `missing_data` strategy. This is because the synonym handling
                     logic (min/max/average of pairwise cognate distances) will
                     result in 1 when one cognate set is empty.
    @return: A symmetric matrix of distances between each pair of languages.
    """

    # Extract unique languages and concepts
    languages = sorted({lang for lang, _ in cognates.keys()})
    concepts = sorted({concept for _, concept in cognates.keys()})

    # Initialize the distance matrix
    dist_matrix = np.zeros((len(languages), len(languages)))

    # Helper function to calculate distance between sets of cognates
    def _calculate_distance(set1: Set[int], set2: Set[int]) -> float:
        """
        Calculates the Jaccard distance between two sets of cognate IDs.
        Jaccard Distance = 1 - (Intersection / Union).

        When used by synonym strategies, this function is typically called with
        singleton sets (e.g., _calculate_distance({c1}, {c2})). In this case:
        - Returns 0 if c1 == c2 (identical cognate IDs).
        - Returns 1 if c1 != c2 (different cognate IDs).

        The condition `if not set1 or not set2: return 0` means that if
        either set is empty, the distance is 0. Standard Jaccard distance
        between an empty set and a non-empty set is 1, and between two
        empty sets is often 0 (or undefined). However, in the current
        `compute_distance_matrix` logic, this specific line is not hit
        when one set is empty and the other is not during synonym comparison,
        as the list comprehension for `all_dists` (or `min_dist`/`max_dist`)
        would be empty, leading to a default distance of 1 for the concept.
        It would apply if, for example, `cognates.get()` returned `None`
        instead of `set()`, and this function was called directly with it.
        """
        if not set1 or not set2:  # Handles two empty sets, or one empty and one not.
            # If both are empty, union is 0, intersection is 0.
            # If one is empty, union is len(other_set), intersection is 0.
            # This specific return 0 deviates from standard Jaccard for one empty set.
            # However, as noted above, the calling context in compute_distance_matrix
            # handles the one-empty-set case differently before this would apply.
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
                    if synonyms == "min":
                        min_dist = min(
                            [
                                _calculate_distance({c1}, {c2})
                                for c1 in cognates1
                                for c2 in cognates2
                            ],
                            default=1,
                        )
                        distances.append(min_dist)
                    elif synonyms == "max":
                        max_dist = max(
                            [
                                _calculate_distance({c1}, {c2})
                                for c1 in cognates1
                                for c2 in cognates2
                            ],
                            default=1,
                        )
                        distances.append(max_dist)
                    elif synonyms == "average":
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
