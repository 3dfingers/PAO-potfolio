import csv


def load_records(filepath: str) -> tuple[list[dict], list[dict]]:
    """Read and validate CRM records from a CSV file.

    Args:
        filepath: Path to the CRM export CSV file.

    Returns:
        A tuple containing:
            - valid_records: List of validated records.
            - error_records: List of rows containing validation errors,
              including their line numbers and original raw data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        UnicodeDecodeError: If the file contains invalid UTF-8 data.
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
                errors.append("id: missing required value")
            else:
                try:
                    record["id"] = int(raw_id.strip())
                except ValueError:
                    errors.append(f"id: cannot convert {raw_id.strip()!r}")

            raw_name = row.get("name")
            if raw_name is None or not raw_name.strip():
                errors.append("name: missing required value")
            else:
                record["name"] = raw_name.strip()

            raw_amount = row.get("amount")
            if raw_amount is None:
                errors.append("amount: missing required value")
            else:
                amount_text = raw_amount.strip()

                if amount_text.lower() in {"", "none", "null", "n/a", "£"}:
                    errors.append("amount: missing required value")
                else:
                    cleaned_amount = amount_text.replace("£", "").replace(",", "")

                    if not cleaned_amount.strip():
                        errors.append("amount: missing required value")
                    else:
                        try:
                            record["amount"] = float(cleaned_amount)
                        except ValueError:
                            errors.append(
                                f"amount: cannot convert {amount_text!r}"
                            )

            raw_status = row.get("status")
            if raw_status is None or not raw_status.strip():
                errors.append("status: missing required value")
            else:
                status = raw_status.strip().lower()

                if status not in {"active", "trial", "churned"}:
                    errors.append(
                        f"status: invalid value {status!r}"
                    )
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