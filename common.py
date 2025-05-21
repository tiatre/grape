from dataclasses import dataclass
from functools import cached_property
from typing import List, FrozenSet, Dict, Set, Tuple
import csv


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
                    print(
                        f"Warning: Line {row_number} in '{input_file}': Skipping row due to missing value(s) "
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
