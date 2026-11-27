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
        A new list containing one record per ID, preserving the original order.
        The input list and its dictionaries are not modified.
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
        valid_records: Records that passed validation.
        error_records: Records containing validation errors.

    Returns:
        A dictionary containing total_rows, valid_count, error_count,
        and errors_by_field.
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
    """Load, deduplicate, summarise, and write pipeline results.

    Args:
        input_csv: Path to the input CSV file.
        output_json: Path to the output JSON file for valid records.

    Returns:
        A summary dictionary describing the loaded records and errors.

    Raises:
        FileNotFoundError: If the input CSV file does not exist.
        OSError: If an input or output file cannot be accessed or written.
        json.JSONDecodeError: If JSON serialization encounters invalid data.
    """
    valid_records, error_records = load_records(input_csv)

    unique_records = deduplicate_by_id(valid_records)
    summary = summarise(valid_records, error_records)

    output_path = Path(output_json)
    errors_path = output_path.with_name(
        f"{output_path.stem}_errors{output_path.suffix}"
    )

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(
            unique_records,
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


def main() -> int:
    """Run the data pipeline from the command line.

    Returns:
        Exit code 0 on success, or 1 if the input file does not exist.
    """
    parser = argparse.ArgumentParser(
        description="Validate, deduplicate, and summarise CSV records."
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
        return 1

    try:
        summary = run_pipeline(args.input, args.output)
    except FileNotFoundError:
        print(
            f"Error: input file '{args.input}' does not exist.",
            file=sys.stderr,
        )
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())