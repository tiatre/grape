#!/usr/bin/env python3

"""
Script to identify and extract lexicore datasets from raw lexibank data.

This script is a pure Python implementation that processes lexicore datasets
from a specified raw directory. It is used to obtain the necessary data
without having to deal with the complexities of installing and using the
full lexibank system.

This script categorizes datasets into:
- Type I: Datasets with cognates in a separate cognates.csv file
- Type II: Datasets with cognates in the forms.csv file (Cognacy column)
"""

from pathlib import Path
import csv
import os
import warnings


# Expected columns for forms.csv
FORMS_COLUMNS = [
    "ID",
    "Parameter_ID",
    "Value",
    "Form",
    "Segments",
    "Cognacy",
    "Loan",
    "Borrowing",
    "Language_ID",
]

# Expected columns for languages.csv
LANGUAGES_COLUMNS = [
    "ID",
    "Name",
    "Glottocode",
    "Glottolog_Name",
    "ISO639P3code",
    "Family",
    "SubGroup",
]

# Expected columns for parameters.csv
PARAMETERS_COLUMNS = ["ID", "Name", "Concepticon_ID", "Concepticon_Gloss"]

# Expected columns for cognates.csv
COGNATES_COLUMNS = [
    "ID",
    "Form_ID",
    "Cognateset_ID",
    "Cognacy_Doubt",
    "Cognate_Detection_Method",
]

# Final output schema
OUTPUT_COLUMNS = [
    "ID",
    "Parameter_ID",
    "Value",
    "Form",
    "Segments",
    "Cognacy",
    "Loan",
    "Borrowing",
    "Language_ID",
    "Language_Name",
    "Glottocode",
    "Glottolog_Name",
    "ISO639P3code",
    "Family",
    "SubGroup",
    "Parameter_Name",
    "Concepticon_ID",
    "Concepticon_Gloss",
    "Cognacy_Doubt",
    "Cognate_Detection_Method",
]


def has_data_in_csv(file_path):
    """Check if CSV file exists and has data rows beyond the header."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Read header
            header = next(reader, None)
            if header is None:
                return False
            # Check if there's at least one data row
            data_row = next(reader, None)
            return data_row is not None
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return False


def has_cognacy_data(forms_csv_path):
    """Check if forms.csv has a Cognacy column with actual data."""
    try:
        with open(forms_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Check if Cognacy column exists
            if not reader.fieldnames or "Cognacy" not in reader.fieldnames:
                return False

            # Check if any row has non-empty Cognacy data
            for row in reader:
                cognacy_value = row.get("Cognacy", "").strip()
                if cognacy_value and cognacy_value.lower() not in [
                    "",
                    "na",
                    "n/a",
                    "null",
                ]:
                    return True

            return False
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return False


def find_column_with_tolerance(fieldnames, target_column):
    """Find column name with tolerance for variations."""
    if not fieldnames:
        return None

    # Exact match first
    if target_column in fieldnames:
        return target_column

    # Case-insensitive search
    target_lower = target_column.lower()
    for field in fieldnames:
        if field.lower() == target_lower:
            return field

    # Common variations
    variations = {
        "Language_ID": ["LanguageID", "Language_Reference", "LanguageReference"],
        "Parameter_ID": ["ParameterID", "Parameter_Reference", "ParameterReference"],
        "ISO639P3code": ["ISO639P3", "ISO", "ISO_code"],
        "Glottolog_Name": ["Glottolog_name", "GlottologName"],
        "SubGroup": ["Sub_Group", "Subgroup"],
        "Concepticon_ID": [
            "ConcepticonID",
            "Concepticon_Reference",
            "ConcepticonReference",
        ],
        "Concepticon_Gloss": ["ConcepticonGloss", "Concepticon_gloss"],
        "Form_ID": ["FormID", "Form_Reference", "FormReference"],
        "Cognateset_ID": [
            "CognatesetID",
            "Cognateset_Reference",
            "CognatesetReference",
        ],
        "Cognacy_Doubt": ["Doubt", "doubt", "Cognacy_doubt"],
        "Cognate_Detection_Method": [
            "CognateDetectionMethod",
            "Cognate_detection_method",
        ],
    }

    if target_column in variations:
        for variant in variations[target_column]:
            if variant in fieldnames:
                return variant
            # Case-insensitive check for variants
            for field in fieldnames:
                if field.lower() == variant.lower():
                    return field

    return None


def load_csv_with_tolerance(file_path, required_columns):
    """Load CSV and map columns with tolerance for variations."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                warnings.warn(f"No fieldnames found in {file_path}")
                return [], {}

            # Read all rows
            rows = list(reader)

    except Exception as e:
        warnings.warn(f"Could not read {file_path}: {e}")
        return [], {}

    column_mapping = {}
    missing_columns = []

    for col in required_columns:
        found_col = find_column_with_tolerance(fieldnames, col)
        if found_col:
            column_mapping[col] = found_col
        else:
            missing_columns.append(col)

    if missing_columns:
        warnings.warn(f"Missing columns in {file_path}: {missing_columns}")

    return rows, column_mapping


def process_type_ii_dataset(dataset_path, output_dir):
    """Process a single Type II dataset and create denormalized CSV."""
    dataset_name = dataset_path.name
    cldf_dir = dataset_path / "cldf"
    forms_csv = cldf_dir / "forms.csv"
    languages_csv = cldf_dir / "languages.csv"
    parameters_csv = cldf_dir / "parameters.csv"

    print(f"Processing Type II dataset: {dataset_name}")

    # Load forms.csv
    forms_rows, forms_mapping = load_csv_with_tolerance(forms_csv, FORMS_COLUMNS)
    if not forms_rows and not forms_mapping:
        warnings.warn(f"Skipping {dataset_name}: Could not load forms.csv")
        return False

    # Load languages.csv
    languages_rows, languages_mapping = load_csv_with_tolerance(
        languages_csv, LANGUAGES_COLUMNS
    )
    if not languages_rows and not languages_mapping:
        warnings.warn(f"Warning for {dataset_name}: Could not load languages.csv")
        languages_rows = []  # Empty list for left join
        languages_mapping = {}

    # Load parameters.csv
    parameters_rows, parameters_mapping = load_csv_with_tolerance(
        parameters_csv, PARAMETERS_COLUMNS
    )
    if not parameters_rows and not parameters_mapping:
        warnings.warn(f"Warning for {dataset_name}: Could not load parameters.csv")
        parameters_rows = []  # Empty list for left join
        parameters_mapping = {}

    # Create a lookup dictionary for languages by ID
    languages_lookup = {}
    if languages_rows:
        id_col = languages_mapping.get("ID", "ID")
        for row in languages_rows:
            lang_id = row.get(id_col, "")
            if lang_id:
                languages_lookup[lang_id] = row

    # Create a lookup dictionary for parameters by ID
    parameters_lookup = {}
    if parameters_rows:
        id_col = parameters_mapping.get("ID", "ID")
        for row in parameters_rows:
            param_id = row.get(id_col, "")
            if param_id:
                parameters_lookup[param_id] = row

    # Process each form and create the final output
    result_rows = []

    for form_row in forms_rows:
        # Start with forms data, mapping to standard column names
        output_row = {}

        # Map forms columns
        for standard_col in FORMS_COLUMNS:
            if standard_col in forms_mapping:
                actual_col = forms_mapping[standard_col]
                output_row[standard_col] = form_row.get(actual_col, "")
            else:
                output_row[standard_col] = ""  # Empty for missing columns

        # Get language data for left join
        language_id = output_row.get("Language_ID", "")
        if language_id and language_id in languages_lookup:
            lang_row = languages_lookup[language_id]

            # Map language columns
            for standard_col in LANGUAGES_COLUMNS:
                if standard_col == "ID":
                    continue  # Skip ID to avoid confusion
                elif standard_col == "Name":
                    # Rename to Language_Name
                    if standard_col in languages_mapping:
                        actual_col = languages_mapping[standard_col]
                        output_row["Language_Name"] = lang_row.get(actual_col, "")
                    else:
                        output_row["Language_Name"] = ""
                else:
                    # Map other language columns directly
                    if standard_col in languages_mapping:
                        actual_col = languages_mapping[standard_col]
                        output_row[standard_col] = lang_row.get(actual_col, "")
                    else:
                        output_row[standard_col] = ""
        else:
            # No language data found, add empty language columns
            output_row["Language_Name"] = ""
            for standard_col in LANGUAGES_COLUMNS:
                if standard_col != "ID" and standard_col != "Name":
                    output_row[standard_col] = ""

        # Get parameter data for left join
        parameter_id = output_row.get("Parameter_ID", "")
        if parameter_id and parameter_id in parameters_lookup:
            param_row = parameters_lookup[parameter_id]

            # Map parameter columns
            for standard_col in PARAMETERS_COLUMNS:
                if standard_col == "ID":
                    continue  # Skip ID to avoid confusion
                elif standard_col == "Name":
                    # Rename to Parameter_Name
                    if standard_col in parameters_mapping:
                        actual_col = parameters_mapping[standard_col]
                        output_row["Parameter_Name"] = param_row.get(actual_col, "")
                    else:
                        output_row["Parameter_Name"] = ""
                else:
                    # Map other parameter columns directly
                    if standard_col in parameters_mapping:
                        actual_col = parameters_mapping[standard_col]
                        output_row[standard_col] = param_row.get(actual_col, "")
                    else:
                        output_row[standard_col] = ""
        else:
            # No parameter data found, add empty parameter columns
            output_row["Parameter_Name"] = ""
            for standard_col in PARAMETERS_COLUMNS:
                if standard_col != "ID" and standard_col != "Name":
                    output_row[standard_col] = ""

        # For Type II datasets, add empty cognate-specific columns
        output_row["Cognacy_Doubt"] = ""
        output_row["Cognate_Detection_Method"] = ""

        result_rows.append(output_row)

    # Save to output directory
    output_file = output_dir / f"{dataset_name}.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()

        for row in result_rows:
            # Ensure all output columns are present
            output_row = {}
            for col in OUTPUT_COLUMNS:
                output_row[col] = row.get(col, "")
            writer.writerow(output_row)

    print(f"  → Saved {len(result_rows)} rows to {output_file}")
    return True


def process_type_i_dataset(dataset_path, output_dir):
    """Process a single Type I dataset and create denormalized CSV."""
    dataset_name = dataset_path.name
    cldf_dir = dataset_path / "cldf"
    forms_csv = cldf_dir / "forms.csv"
    languages_csv = cldf_dir / "languages.csv"
    parameters_csv = cldf_dir / "parameters.csv"
    cognates_csv = cldf_dir / "cognates.csv"

    print(f"Processing Type I dataset: {dataset_name}")

    # Load forms.csv
    forms_rows, forms_mapping = load_csv_with_tolerance(forms_csv, FORMS_COLUMNS)
    if not forms_rows and not forms_mapping:
        warnings.warn(f"Skipping {dataset_name}: Could not load forms.csv")
        return False

    # Load languages.csv
    languages_rows, languages_mapping = load_csv_with_tolerance(
        languages_csv, LANGUAGES_COLUMNS
    )
    if not languages_rows and not languages_mapping:
        warnings.warn(f"Warning for {dataset_name}: Could not load languages.csv")
        languages_rows = []  # Empty list for left join
        languages_mapping = {}

    # Load parameters.csv
    parameters_rows, parameters_mapping = load_csv_with_tolerance(
        parameters_csv, PARAMETERS_COLUMNS
    )
    if not parameters_rows and not parameters_mapping:
        warnings.warn(f"Warning for {dataset_name}: Could not load parameters.csv")
        parameters_rows = []  # Empty list for left join
        parameters_mapping = {}

    # Load cognates.csv
    cognates_rows, cognates_mapping = load_csv_with_tolerance(
        cognates_csv, COGNATES_COLUMNS
    )
    if not cognates_rows and not cognates_mapping:
        warnings.warn(f"Warning for {dataset_name}: Could not load cognates.csv")
        cognates_rows = []  # Empty list for left join
        cognates_mapping = {}

    # Create a lookup dictionary for languages by ID
    languages_lookup = {}
    if languages_rows:
        id_col = languages_mapping.get("ID", "ID")
        for row in languages_rows:
            lang_id = row.get(id_col, "")
            if lang_id:
                languages_lookup[lang_id] = row

    # Create a lookup dictionary for parameters by ID
    parameters_lookup = {}
    if parameters_rows:
        id_col = parameters_mapping.get("ID", "ID")
        for row in parameters_rows:
            param_id = row.get(id_col, "")
            if param_id:
                parameters_lookup[param_id] = row

    # Create a lookup dictionary for cognates by Form_ID (handling multiple cognates per form)
    cognates_lookup = {}
    if cognates_rows:
        form_id_col = cognates_mapping.get("Form_ID", "Form_ID")
        for row in cognates_rows:
            form_id = row.get(form_id_col, "")
            if form_id:
                if form_id not in cognates_lookup:
                    cognates_lookup[form_id] = []
                cognates_lookup[form_id].append(row)

    # Process each form and create the final output
    result_rows = []
    multiple_cognates_warning_logged = set()

    for form_row in forms_rows:
        # Start with forms data, mapping to standard column names
        base_output_row = {}

        # Map forms columns
        for standard_col in FORMS_COLUMNS:
            if standard_col in forms_mapping:
                actual_col = forms_mapping[standard_col]
                base_output_row[standard_col] = form_row.get(actual_col, "")
            else:
                base_output_row[standard_col] = ""  # Empty for missing columns

        # Get language data for left join
        language_id = base_output_row.get("Language_ID", "")
        if language_id and language_id in languages_lookup:
            lang_row = languages_lookup[language_id]

            # Map language columns
            for standard_col in LANGUAGES_COLUMNS:
                if standard_col == "ID":
                    continue  # Skip ID to avoid confusion
                elif standard_col == "Name":
                    # Rename to Language_Name
                    if standard_col in languages_mapping:
                        actual_col = languages_mapping[standard_col]
                        base_output_row["Language_Name"] = lang_row.get(actual_col, "")
                    else:
                        base_output_row["Language_Name"] = ""
                else:
                    # Map other language columns directly
                    if standard_col in languages_mapping:
                        actual_col = languages_mapping[standard_col]
                        base_output_row[standard_col] = lang_row.get(actual_col, "")
                    else:
                        base_output_row[standard_col] = ""
        else:
            # No language data found, add empty language columns
            base_output_row["Language_Name"] = ""
            for standard_col in LANGUAGES_COLUMNS:
                if standard_col != "ID" and standard_col != "Name":
                    base_output_row[standard_col] = ""

        # Get parameter data for left join
        parameter_id = base_output_row.get("Parameter_ID", "")
        if parameter_id and parameter_id in parameters_lookup:
            param_row = parameters_lookup[parameter_id]

            # Map parameter columns
            for standard_col in PARAMETERS_COLUMNS:
                if standard_col == "ID":
                    continue  # Skip ID to avoid confusion
                elif standard_col == "Name":
                    # Rename to Parameter_Name
                    if standard_col in parameters_mapping:
                        actual_col = parameters_mapping[standard_col]
                        base_output_row["Parameter_Name"] = param_row.get(
                            actual_col, ""
                        )
                    else:
                        base_output_row["Parameter_Name"] = ""
                else:
                    # Map other parameter columns directly
                    if standard_col in parameters_mapping:
                        actual_col = parameters_mapping[standard_col]
                        base_output_row[standard_col] = param_row.get(actual_col, "")
                    else:
                        base_output_row[standard_col] = ""
        else:
            # No parameter data found, add empty parameter columns
            base_output_row["Parameter_Name"] = ""
            for standard_col in PARAMETERS_COLUMNS:
                if standard_col != "ID" and standard_col != "Name":
                    base_output_row[standard_col] = ""

        # Get cognate data for left join
        form_id = base_output_row.get("ID", "")
        if form_id and form_id in cognates_lookup:
            cognate_entries = cognates_lookup[form_id]

            # Check for multiple cognates and log warning
            if (
                len(cognate_entries) > 1
                and dataset_name not in multiple_cognates_warning_logged
            ):
                warnings.warn(
                    f"Dataset {dataset_name}: Form {form_id} has {len(cognate_entries)} cognate assignments, creating separate rows"
                )
                multiple_cognates_warning_logged.add(dataset_name)

            # Create one row for each cognate assignment
            for cognate_row in cognate_entries:
                output_row = base_output_row.copy()

                # Map cognate columns, filling Cognacy with Cognateset_ID
                for standard_col in COGNATES_COLUMNS:
                    if standard_col == "ID" or standard_col == "Form_ID":
                        continue  # Skip ID and Form_ID to avoid confusion
                    elif standard_col == "Cognateset_ID":
                        # Fill the Cognacy field with Cognateset_ID
                        if standard_col in cognates_mapping:
                            actual_col = cognates_mapping[standard_col]
                            output_row["Cognacy"] = cognate_row.get(actual_col, "")
                        else:
                            output_row["Cognacy"] = ""
                    elif standard_col == "Cognacy_Doubt":
                        # Map to Cognacy_Doubt
                        if standard_col in cognates_mapping:
                            actual_col = cognates_mapping[standard_col]
                            output_row["Cognacy_Doubt"] = cognate_row.get(
                                actual_col, ""
                            )
                        else:
                            output_row["Cognacy_Doubt"] = ""
                    elif standard_col == "Cognate_Detection_Method":
                        # Map directly
                        if standard_col in cognates_mapping:
                            actual_col = cognates_mapping[standard_col]
                            output_row["Cognate_Detection_Method"] = cognate_row.get(
                                actual_col, ""
                            )
                        else:
                            output_row["Cognate_Detection_Method"] = ""

                result_rows.append(output_row)
        else:
            # No cognate data found, add empty cognate columns
            output_row = base_output_row.copy()
            # Keep original Cognacy value from forms.csv (might be empty)
            output_row["Cognacy_Doubt"] = ""
            output_row["Cognate_Detection_Method"] = ""
            result_rows.append(output_row)

    # Save to output directory
    output_file = output_dir / f"{dataset_name}.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()

        for row in result_rows:
            # Ensure all output columns are present
            output_row = {}
            for col in OUTPUT_COLUMNS:
                output_row[col] = row.get(col, "")
            writer.writerow(output_row)

    print(f"  → Saved {len(result_rows)} rows to {output_file}")
    return True


def collect_lexicore_data(
    raw_directory,
    type_i_datasets,
    type_ii_datasets,
    output_directory="lexicore_datasets",
):
    """Collect and process all lexicore datasets (both Type I and Type II)."""
    raw_path = Path(raw_directory)
    output_path = Path(output_directory)

    # Create output directory
    output_path.mkdir(exist_ok=True)

    print(f"\nCollecting lexicore data...")
    print(f"Output directory: {output_path.absolute()}")
    print("=" * 60)

    successful = 0
    failed = 0

    # Process Type I datasets
    for dataset_name in type_i_datasets:
        dataset_path = raw_path / dataset_name
        try:
            if process_type_i_dataset(dataset_path, output_path):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing Type I {dataset_name}: {e}")
            failed += 1

    # Process Type II datasets
    for dataset_name in type_ii_datasets:
        dataset_path = raw_path / dataset_name
        try:
            if process_type_ii_dataset(dataset_path, output_path):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing Type II {dataset_name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Lexicore data collection complete:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {successful + failed}")

    return successful, failed


def identify_lexicore_datasets(raw_directory):
    """
    Identify lexicore datasets in the raw directory.

    Returns:
        tuple: (type_i_datasets, type_ii_datasets)
    """
    raw_path = Path(raw_directory)
    type_i_datasets = []
    type_ii_datasets = []
    skipped_datasets = []

    if not raw_path.exists():
        print(f"Error: Raw directory '{raw_directory}' does not exist.")
        return type_i_datasets, type_ii_datasets, skipped_datasets

    # Iterate over all directories in raw/
    for item in sorted(raw_path.iterdir()):
        if not item.is_dir():
            continue

        dataset_name = item.name
        cldf_dir = item / "cldf"

        # Skip if no cldf directory
        if not cldf_dir.exists() or not cldf_dir.is_dir():
            skipped_datasets.append(f"{dataset_name} (no cldf directory)")
            continue

        cognates_csv = cldf_dir / "cognates.csv"
        forms_csv = cldf_dir / "forms.csv"

        # Check for Type I: cognates.csv with data, but no cognacy data in forms.csv
        if has_data_in_csv(cognates_csv):
            # Only classify as Type I if forms.csv doesn't have cognacy data
            if not has_cognacy_data(forms_csv):
                type_i_datasets.append(dataset_name)
                print(f"Type I:  {dataset_name}")
                continue
            else:
                # Has both cognates.csv and cognacy in forms.csv - skip to avoid duplication
                skipped_datasets.append(
                    f"{dataset_name} (has both cognates.csv and cognacy in forms.csv)"
                )
                continue

        # Check for Type II: forms.csv with Cognacy column containing data
        if has_cognacy_data(forms_csv):
            type_ii_datasets.append(dataset_name)
            print(f"Type II: {dataset_name}")
            continue

        # Neither type - skip
        skipped_datasets.append(f"{dataset_name} (no cognacy data)")

    return type_i_datasets, type_ii_datasets, skipped_datasets


def main():
    """Main function to run the dataset identification and data collection."""
    raw_directory = "raw"

    print("Identifying lexicore datasets...")
    print("=" * 50)
    print(f"Looking in directory: {os.path.abspath(raw_directory)}")

    type_i, type_ii, skipped = identify_lexicore_datasets(raw_directory)

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Type I datasets (cognates.csv):  {len(type_i)}")
    print(f"Type II datasets (forms.csv):    {len(type_ii)}")
    print(f"Skipped datasets:                {len(skipped)}")
    print(f"Total lexicore datasets:         {len(type_i) + len(type_ii)}")

    # Collect lexicore data
    if type_i or type_ii:
        successful, failed = collect_lexicore_data(raw_directory, type_i, type_ii)
    else:
        print("\nNo lexicore datasets found to process.")
        successful, failed = 0, 0

    # Store results for later use
    results = {
        "type_i": type_i,
        "type_ii": type_ii,
        "skipped": skipped,
        "collection_stats": {"successful": successful, "failed": failed},
    }

    return results


if __name__ == "__main__":
    results = main()
