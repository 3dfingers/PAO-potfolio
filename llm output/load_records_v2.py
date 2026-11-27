import csv
import math


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