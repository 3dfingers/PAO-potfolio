import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def deduplicate_by_id(records: list[dict]) -> list[dict]:
    """Return records with duplicate IDs removed, keeping the first occurrence.

    Args:
        records: List of valid records.

    Returns:
        A new list containing the first record for each ID.
    """
    seen_ids = set()
    unique_records = []

    for record in records:
        record_id = record["id"]

        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)

    return unique_records


def summarise(
    valid_records: list[dict],
    error_records: list[dict],
) -> dict:
    """Summarise valid records and validation errors.

    Args:
        valid_records: List of valid records.
        error_records: List of error records.

    Returns:
        A summary containing total rows, valid count, error count,
        and counts of errors grouped by field.
    """
    errors_by_field = Counter()

    for error_record in error_records:
        for error_message in error_record["errors"]:
            field_name = error_message.split(":", 1)[0]
            errors_by_field[field_name] += 1

    valid_count = len(valid_records)
    error_count = len(error_records)

    return {
        "total_rows": valid_count + error_count,
        "valid_count": valid_count,
        "error_count": error_count,
        "errors_by_field": dict(errors_by_field),
    }


def run_pipeline(input_csv: str, output_json: str) -> dict:
    """Load, deduplicate, summarise, and write pipeline records.

    Args:
        input_csv: Path to the input CSV file.
        output_json: Path to the output JSON file for valid records.

    Returns:
        Summary of the deduplicated valid records and error records.

    Raises:
        FileNotFoundError: If the input CSV file does not exist.
        OSError: If an input or output file cannot be accessed.
        ValueError: If JSON serialization fails.
    """
    valid_records, error_records = load_records(input_csv)

    deduplicated_records = deduplicate_by_id(valid_records)

    summary = summarise(deduplicated_records, error_records)

    output_path = Path(output_json)
    errors_path = output_path.with_name(
        f"{output_path.stem}_errors{output_path.suffix}"
    )

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(
            deduplicated_records,
            output_file,
            ensure_ascii=False,
            indent=2,
        )

    with errors_path.open("w", encoding="utf-8") as errors_file:
        json.dump(
            error_records,
            errors_file,
            ensure_ascii=False,
            indent=2,
        )

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load, validate, deduplicate, and summarise CSV records."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output JSON file.",
    )

    args = parser.parse_args()

    if not Path(args.input).is_file():
        print(
            f"Error: input file '{args.input}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        summary = run_pipeline(args.input, args.output)
    except FileNotFoundError:
        print(
            f"Error: input file '{args.input}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps(summary, ensure_ascii=False, indent=2))