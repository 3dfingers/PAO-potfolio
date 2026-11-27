# Integrator check: LLM-written docstring for process_contact (27 Nov 2026)

LLM docstring saved in: llm_outputs/process_contact_docstring_v1.txt

| Claim in docstring | Actual behaviour | Verdict |
|---|---|---|
| Does not modify the input | Builds a new dict; run_records.py shows input unchanged for all 5 records | Accurate |
| Requires name, email, phone | Loops over those three keys | Accurate |
| Returns first, last, email_ok, phone | Exactly those keys | Accurate |
| Raises ValueError for missing field / name / phone errors, with "name: " / "phone: " prefixes | Confirmed | Accurate |
| Lists ONLY ValueError | process_contact(None) raises TypeError | INCOMPLETE |
| (not mentioned) | An invalid email does not raise; it gives email_ok = False | Omission |

Evidence:
```
python -c "from contacts import process_contact; process_contact(None)"
TypeError: argument of type 'NoneType' is not a container or iterable
```

Verdict: the docstring describes the intended behaviour, not all of the actual behaviour. My spec also does not say what happens with a non-dict input (spec gap).