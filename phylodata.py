from typing import Dict, Tuple, Set


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
        with open(input_file, "r") as f_in:
            # Skip the header line
            next(f_in)

            for line in f_in:
                # Split the line by tabs and ensure it contains exactly three parts
                parts = line.strip().split("\t")
                if len(parts) != 3:
                    raise ValueError(
                        "Each line must contain exactly three tab-separated fields."
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
