# Trace v1: load_records (before running), 27 Nov 2026

| File line | Row | My prediction | What the code does (by reading it) | Match? |
|---|---|---|---|---|
| 2 | 1001,Ada Kierkegaard,1119.94,  CHURNED   | error | all fields pass; status stripped + lowercased to "churned"; VALID | No: I assumed padding/caps cause rejection, but the code cleans them |
| 10 | 1009,Donald Schmidt,£4423.99, | valid | status empty, gives "status: missing required value"; ERROR | No: I missed the empty status |
| 62 | 1060,Claude Johnson,abc,  Trial   | (not predicted) | float("abc") raises ValueError, gives "amount: cannot convert 'abc'"; ERROR | n/a |

## Problems spotted by reading the code
1. load_records: float() accepts "nan" and "inf", so an amount of "nan" would be marked VALID (silent wrong answer). json.dump would then write NaN, which is not valid JSON. Not covered by my schema (spec gap).
2. run_pipeline: summary is built from valid_records BEFORE deduplication, but clean.json holds the deduplicated list. With duplicate ids, the summary count and the file would disagree. My spec did not say which list to summarise (spec gap).
3. run_pipeline docstring claims it can raise json.JSONDecodeError, which only happens when reading JSON, not writing it.
# Repair round 1: nan/inf amounts (27 Nov 2026)
- Defect: float() accepted "nan"/"inf", so those rows were marked VALID and would be written as NaN (invalid JSON). Found by reading v1 code.
- Spec first: amount rule now rejects nan/inf. New test test_nan_and_inf_amounts_rejected: 4 failed, 40 passed against v1.
- Prompt v2 added: "Do NOT accept nan, inf or -inf ... Only finite numbers are valid."
- v2 code: checks the three words AND adds math.isfinite(), a general safety net that also catches "Infinity" and "1e999", which I did not list.
- Side effect: v2 reworded error messages (e.g. "id: missing required value" became "id: missing") without being asked.
- Result: 44 passed.
# Repair round 2: summary after dedup (27 Nov 2026)
- Defect: run_pipeline passed valid_records (before dedup) to summarise, while clean.json held the deduplicated list. Found by reading v1 code.
- Spec first; new test test_run_pipeline_summary_matches_file_after_dedup failed: summary said 2, file had 1.
- Prompt v2 added: "pass the DEDUPLICATED valid records to summarise".
- v2 fixed it, but also removed main(), and quietly corrected the wrong JSONDecodeError docstring.
- Result: 45 passed.

# Real-file run
python pipeline.py --input data/messy_crm_v2.csv --output clean.json
total_rows 1000, valid 557, errors 443 (amount 85, status 347, name 28)

# Tester finding: unquoted thousands comma (line 22 and 176 others)
Unquoted "£2,683.75" splits into amount "£2" and status "683.75". The amount check accepts "£2" as 2.0 with no error. The row is quarantined only because "683.75" fails the status rule, so the error is reported against the wrong field. 177 of the 347 status errors are really amount errors. With an optional status, these rows would be silently accepted with wrong amounts.