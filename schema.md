# Unit 2 Schema and Specification: messy_crm_v2.csv

Author: Ndubuisi Samuel · Role: Solo (Architect, Builder, Integrator, Tester) · Written 27 Nov 2026, before any code

## 1. Validation schema (one rule per field)

| Field | Type after conversion | Required | Rules | Decision / why |
|---|---|---|---|---|
| id | int | yes | strip spaces; must convert to int | ids are the key for deduplication |
| name | str | yes | strip spaces; must not be empty or only spaces | a record with no name is unusable |
| amount | float | yes | strip spaces; remove "£" and ","; empty, "none", "NULL", "N/A" or "£" alone = missing = reject; non-numeric (e.g. "abc") = reject | **negative amounts are ACCEPTED** (could be refunds); **0.0 is VALID** |
| status | str | yes | strip spaces; convert to lowercase; must be one of: active, trial, churned | **empty or missing status = REJECT**; **any other value (unknown, suspended, pending_approval, archived) = REJECT** |

Other file rules:
- **Extra columns** (e.g. ",EXTRA_FIELD") are **IGNORED**: the row is still validated on its 4 real fields.
- **Blank lines** are skipped.
- **Encoding:** open with `encoding="utf-8-sig"` (removes the BOM) and `newline=""`. A file that is not valid UTF-8 must fail loudly (UnicodeDecodeError), never be silently mis-read.

## 2. Function specifications

### load_records(filepath: str) -> tuple[list[dict], list[dict]]
- Reads the CSV with csv.DictReader and checks EVERY row against the schema.
- Returns (valid_records, error_records).
- A valid record is a NEW dict: {"id": int, "name": str, "amount": float, "status": str}.
- An error record is: {"line": int, "errors": [str, ...], "raw": dict}
  - "line" = the row's line number in the file (reader.line_num; header is line 1; blank lines count)
  - "errors" lists EVERY problem in the row, not just the first. Each message starts with the field name, e.g. "amount: cannot convert 'abc'"
  - "raw" = the row exactly as read
- Every data row ends up in exactly one of the two lists. Nothing disappears.
- Raises FileNotFoundError if the file does not exist.
- Must NOT use a bare except. Must NOT remove items from a list while looping over it.

### deduplicate_by_id(records: list[dict]) -> list[dict]
- Returns a NEW list with one record per id. **If an id appears twice, the FIRST one is kept**, even if other fields differ.
- **Same name with a different id = different people** (not duplicates).
- Must NOT change the input list or its dicts.

### summarise(valid_records: list[dict], error_records: list[dict]) -> dict
- Returns {"total_rows": int, "valid_count": int, "error_count": int, "errors_by_field": {field: count}}
- errors_by_field counts each error message by its field name (the text before the first ":").
- (Deliberate change from the guide's one-argument signature: the summary needs both lists to give a total.)

### run_pipeline(input_csv: str, output_json: str) -> dict
- load_records → deduplicate_by_id → summarise.
- Writes valid records to output_json, and error records to the same name with "_errors" added (clean.json → clean_errors.json).
- JSON written with ensure_ascii=False, indent=2, encoding="utf-8".
- Returns the summary dict.

### Command line
- `python pipeline.py --input data/messy_crm_v2.csv --output clean.json`
- Prints the summary.
- Missing input file → prints a friendly message (no traceback) and exits with code 1.

## Change log
| Date | Change | Reason |
|---|---|---|
| 27 Nov 2026 | amount: "nan" and "inf" are rejected | Reading the v1 code showed float() accepts "nan"/"inf", so they would be marked valid and written as invalid JSON (NaN) |