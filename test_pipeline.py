import json
import subprocess
import sys

import pytest

from pipeline import load_records, deduplicate_by_id, summarise, run_pipeline

HEADER = "id,name,amount,status\n"


def write_csv(tmp_path, body, bom=False, name="data.csv"):
    """Write a small test CSV file and return its path as a string."""
    path = tmp_path / name
    data = (HEADER + body).encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)
    return str(path)


# ---------- load_records: valid rows ----------

def test_valid_row_is_converted(tmp_path):
    path = write_csv(tmp_path, "1001,Ada Lovelace,250.50,active\n")
    valid, errors = load_records(path)
    assert valid == [{"id": 1001, "name": "Ada Lovelace", "amount": 250.5, "status": "active"}]
    assert errors == []


def test_quoted_pound_amount_with_thousands_comma(tmp_path):
    path = write_csv(tmp_path, '1001,Ada,"£1,234.50",active\n')
    valid, errors = load_records(path)
    assert valid[0]["amount"] == 1234.5


def test_padded_amount_and_mixed_case_status(tmp_path):
    path = write_csv(tmp_path, "1001,Ada, 3492.21 ,  CHURNED  \n")
    valid, errors = load_records(path)
    assert valid[0]["amount"] == 3492.21
    assert valid[0]["status"] == "churned"


def test_quoted_name_with_comma_and_non_ascii(tmp_path):
    path = write_csv(tmp_path, '1001,"Dubois, Søren",10.00,trial\n')
    valid, errors = load_records(path)
    assert valid[0]["name"] == "Dubois, Søren"


def test_negative_amount_accepted(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,-17.09,active\n")
    valid, errors = load_records(path)
    assert valid[0]["amount"] == -17.09


def test_zero_amount_accepted(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,0.00,active\n")
    valid, errors = load_records(path)
    assert valid[0]["amount"] == 0.0
    assert errors == []


def test_extra_column_is_ignored(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,10.00,active,EXTRA_FIELD\n")
    valid, errors = load_records(path)
    assert valid == [{"id": 1001, "name": "Ada", "amount": 10.0, "status": "active"}]


def test_bom_is_handled(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,10.00,active\n", bom=True)
    valid, errors = load_records(path)
    assert valid[0]["id"] == 1001
    assert errors == []


# ---------- load_records: rows that must be quarantined ----------

def test_empty_amount_rejected_with_line_number(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,,active\n")
    valid, errors = load_records(path)
    assert valid == []
    assert errors[0]["line"] == 2
    assert errors[0]["errors"][0].startswith("amount")


def test_non_numeric_amount_rejected(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,abc,active\n")
    valid, errors = load_records(path)
    assert valid == []
    assert errors[0]["errors"][0].startswith("amount")


@pytest.mark.parametrize("missing", ["none", "NULL", "N/A", "£"])
def test_missing_amount_words_rejected(tmp_path, missing):
    path = write_csv(tmp_path, f"1001,Ada,{missing},active\n")
    valid, errors = load_records(path)
    assert valid == []
    assert len(errors) == 1


def test_blank_name_rejected(tmp_path):
    path = write_csv(tmp_path, '1001,"   ",10.00,active\n')
    valid, errors = load_records(path)
    assert valid == []
    assert errors[0]["errors"][0].startswith("name")


@pytest.mark.parametrize("status", ["unknown", "suspended", "pending_approval", "archived", ""])
def test_bad_status_rejected(tmp_path, status):
    path = write_csv(tmp_path, f"1001,Ada,10.00,{status}\n")
    valid, errors = load_records(path)
    assert valid == []
    assert errors[0]["errors"][0].startswith("status")


def test_missing_status_column_rejected(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,10.00\n")
    valid, errors = load_records(path)
    assert valid == []
    assert errors[0]["errors"][0].startswith("status")


def test_non_integer_id_rejected(tmp_path):
    path = write_csv(tmp_path, "abc,Ada,10.00,active\n")
    valid, errors = load_records(path)
    assert valid == []
    assert errors[0]["errors"][0].startswith("id")


def test_all_errors_in_a_row_are_listed(tmp_path):
    path = write_csv(tmp_path, '1001,"   ",abc,unknown\n')
    valid, errors = load_records(path)
    assert len(errors[0]["errors"]) == 3


def test_error_record_keeps_raw_row(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,abc,active\n")
    valid, errors = load_records(path)
    assert errors[0]["raw"]["amount"] == "abc"


def test_unquoted_thousands_comma_is_not_silently_accepted(tmp_path):
    # £2,683.75 without quotes splits into amount "£2" and status "683.75"
    path = write_csv(tmp_path, "1001,Ada,£2,683.75,  TRIAL  \n")
    valid, errors = load_records(path)
    assert valid == []
    assert len(errors) == 1


# ---------- load_records: whole-file cases ----------

def test_header_only_file(tmp_path):
    path = write_csv(tmp_path, "")
    assert load_records(path) == ([], [])


def test_blank_lines_skipped_and_line_numbers_still_correct(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,10.00,active\n\n1002,Bob,abc,active\n")
    valid, errors = load_records(path)
    assert len(valid) == 1
    assert errors[0]["line"] == 4


def test_adjacent_bad_rows_are_both_quarantined(tmp_path):
    path = write_csv(tmp_path, "1001,Ada,,active\n1002,Bob,abc,trial\n1003,Cy,5.00,active\n")
    valid, errors = load_records(path)
    assert len(errors) == 2
    assert len(valid) == 1


def test_every_row_is_accounted_for(tmp_path):
    body = ("1001,Ada,10.00,active\n1002,Bob,abc,trial\n1003,,5.00,active\n"
            "1004,Cy,7.00,unknown\n1005,Di,£8.00,churned\n")
    path = write_csv(tmp_path, body)
    valid, errors = load_records(path)
    assert len(valid) + len(errors) == 5


def test_every_row_a_copy_of_the_header(tmp_path):
    path = write_csv(tmp_path, "id,name,amount,status\nid,name,amount,status\n")
    valid, errors = load_records(path)
    assert valid == []
    assert len(errors) == 2


def test_non_utf8_file_fails_loudly(tmp_path):
    path = tmp_path / "latin1.csv"
    path.write_bytes((HEADER + "1001,José,10.00,active\n").encode("latin-1"))
    with pytest.raises(UnicodeDecodeError):
        load_records(str(path))


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_records(str(tmp_path / "does_not_exist.csv"))


# ---------- deduplicate_by_id ----------

def test_exact_duplicates_removed():
    rec = {"id": 1, "name": "Ada", "amount": 1.0, "status": "active"}
    assert deduplicate_by_id([rec, dict(rec)]) == [rec]


def test_duplicate_differing_in_one_field_keeps_first():
    first = {"id": 1, "name": "Ada", "amount": 1.0, "status": "active"}
    second = {"id": 1, "name": "Ada", "amount": 99.0, "status": "active"}
    assert deduplicate_by_id([first, second]) == [first]


def test_same_name_different_id_both_kept():
    a = {"id": 1, "name": "Alan Turing", "amount": 1.0, "status": "active"}
    b = {"id": 2, "name": "Alan Turing", "amount": 2.0, "status": "trial"}
    assert deduplicate_by_id([a, b]) == [a, b]


def test_dedup_does_not_change_input():
    records = [{"id": 1, "name": "Ada", "amount": 1.0, "status": "active"},
               {"id": 1, "name": "Ada", "amount": 2.0, "status": "active"}]
    before = [dict(r) for r in records]
    deduplicate_by_id(records)
    assert records == before


# ---------- summarise ----------

def test_summarise_counts():
    valid = [{"id": 1}, {"id": 2}]
    errors = [{"line": 3, "errors": ["amount: x", "status: y"], "raw": {}},
              {"line": 4, "errors": ["amount: z"], "raw": {}}]
    assert summarise(valid, errors) == {
        "total_rows": 4,
        "valid_count": 2,
        "error_count": 2,
        "errors_by_field": {"amount": 2, "status": 1},
    }


# ---------- run_pipeline ----------

def test_run_pipeline_writes_both_json_files(tmp_path):
    path = write_csv(tmp_path, '1001,"Dubois, Søren",10.00,active\n1002,Bob,abc,trial\n')
    out = tmp_path / "clean.json"
    summary = run_pipeline(path, str(out))
    clean = json.loads(out.read_text(encoding="utf-8"))
    errs = json.loads((tmp_path / "clean_errors.json").read_text(encoding="utf-8"))
    assert len(clean) == 1 and len(errs) == 1
    assert summary["valid_count"] == 1


def test_run_pipeline_keeps_non_ascii_readable(tmp_path):
    path = write_csv(tmp_path, '1001,"Dubois, Søren",10.00,active\n')
    out = tmp_path / "clean.json"
    run_pipeline(path, str(out))
    assert "Søren" in out.read_text(encoding="utf-8")


# ---------- command line ----------

def test_cli_missing_file_gives_friendly_message(tmp_path):
    result = subprocess.run(
        [sys.executable, "pipeline.py", "--input", str(tmp_path / "nope.csv"),
         "--output", str(tmp_path / "out.json")],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr