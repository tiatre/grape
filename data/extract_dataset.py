import argparse
import csv
import sys
from unidecode import unidecode


def slug(text):
    # Trim text
    text = text.strip()
    # Convert Unicode characters to ASCII
    text = unidecode(text)
    # Replace dashes with nothing and spaces with underscores
    text = text.replace("-", "").replace(" ", "_")
    # Replace multiple underscores with a single underscore
    text = "_".join(filter(None, text.split("_")))
    # Remove all characters except alphanumeric and underscores
    text = "".join(char for char in text if char.isalnum() or char in "._")
    return text


def filter_and_transform_data(input_filename, dataset_name, filter_languages=None):
    output_filename = f"{dataset_name}.tsv"
    languages = set()
    concepts = set()

    with open(input_filename, "r", newline="", encoding="utf-8") as infile, open(
        output_filename, "w", newline="", encoding="utf-8"
    ) as outfile:
        tsv_reader = csv.DictReader(infile, delimiter="\t")
        fieldnames = ["Language", "Parameter", "Cognateset"]
        tsv_writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter="\t")

        tsv_writer.writeheader()

        for row in tsv_reader:
            if row["Dataset"] == dataset_name:
                # Apply the slug function to fields
                row["Language"] = slug(row["Language"])
                row["Parameter"] = slug(row["Parameter"])
                row["Cognateset"] = slug(row["Cognateset"])

                # Split all cognateset entries at dots and keep only the second and third parts
                row["Cognateset"] = ".".join(row["Cognateset"].split(".")[1:])

                # Filtering by language if specified
                if (
                    filter_languages is not None
                    and row["Language"] not in filter_languages
                ):
                    continue

                # Write only the selected fields to the new file
                tsv_writer.writerow(
                    {
                        "Language": row["Language"],
                        "Parameter": row["Parameter"],
                        "Cognateset": row["Cognateset"],
                    }
                )

                # Collecting distinct languages and concepts
                languages.add(row["Language"])
                concepts.add(row["Parameter"])

    # Sorting and printing the results
    sorted_languages = sorted(languages)
    sorted_concepts = sorted(concepts)

    print(f"Distinct Languages: {len(sorted_languages)}")
    print("Languages:", sorted_languages)
    print(f"Distinct Concepts: {len(sorted_concepts)}")
    print("Concepts:", sorted_concepts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filter and transform dataset information."
    )
    parser.add_argument("dataset_name", help="Name of the dataset to process")
    parser.add_argument(
        "--languages", help="Optional; semicolon-separated list of languages to include"
    )

    args = parser.parse_args()

    filter_languages = args.languages.split(";") if args.languages else None

    filter_and_transform_data(
        "arcaverborum_corecog.20240604.tsv", args.dataset_name, filter_languages
    )
