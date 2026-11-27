import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path


def load_records(filepath: str) -> tuple[list[dict], list[dict]]:
    """Read and validate CRM records from a CSV file.

    Args:
        filepath: Path to the CRM export CSV file.

    Returns:
        A tuple containing:
            - valid_records: List of validated records.
            - error_records: List of rows containing validation errors, with
              their line numbers, error messages, and original raw data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        UnicodeDecodeError: If the file is not valid UTF-8.
        csv.Error: If the CSV file contains malformed CSV data.
    """
    valid_records: list[dict] = []
    error_records: list[dict] = []

    with open(filepath, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, restkey="_extra")

        for row in reader:
            errors: list[str] = []
            record: dict = {}

            raw_id = row.get("id")
            if raw_id is None or not raw_id.strip():
                errors.append("id: missing")
            else:
                try:
                    record["id"] = int(raw_id.strip())
                except ValueError:
                    errors.append(f"id: cannot convert {raw_id.strip()!r}")

            raw_name = row.get("name")
            if raw_name is None or not raw_name.strip():
                errors.append("name: missing or empty")
            else:
                record["name"] = raw_name.strip()

            raw_amount = row.get("amount")
            if raw_amount is None:
                errors.append("amount: missing")
            else:
                cleaned_amount = raw_amount.strip()

                if cleaned_amount.lower() in {"", "none", "null", "n/a", "£"}:
                    errors.append("amount: missing")
                else:
                    cleaned_amount = cleaned_amount.replace("£", "").replace(",", "")

                    if cleaned_amount.lower() in {"nan", "inf", "-inf"}:
                        errors.append(
                            f"amount: cannot convert {raw_amount.strip()!r}"
                        )
                    else:
                        try:
                            amount = float(cleaned_amount)

                            if not math.isfinite(amount):
                                errors.append(
                                    f"amount: cannot convert {raw_amount.strip()!r}"
                                )
                            else:
                                record["amount"] = amount
                        except ValueError:
                            errors.append(
                                f"amount: cannot convert {raw_amount.strip()!r}"
                            )

            raw_status = row.get("status")
            if raw_status is None or not raw_status.strip():
                errors.append("status: missing")
            else:
                status = raw_status.strip().lower()

                if status not in {"active", "trial", "churned"}:
                    errors.append(f"status: invalid value {status!r}")
                else:
                    record["status"] = status

            if errors:
                error_records.append(
                    {
                        "line": reader.line_num,
                        "errors": errors,
                        "raw": dict(row),
                    }
                )
            else:
                valid_records.append(record)

    return valid_records, error_records


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