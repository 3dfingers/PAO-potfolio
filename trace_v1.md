# Trace v1: parse_name (before running)

| Input | My prediction | What the code actually does (by reading it) | Match? |
|---|---|---|---|
| "Ada Lovelace" | returns {"first": "Ada", "last": "Lovelace"} | returns {"first": "Ada", "last": "Lovelace"} | Yes |
| "Cher" | raises ValueError (only one name) | split() gives 1 word, so raises ValueError | Yes |
| "  ada   lovelace  " | raises ValueError (no capital letter) | split() removes spaces, capitalize()/title() add capitals, returns {"first": "Ada", "last": "Lovelace"} | No: I assumed it checked capitals, but it fixes them |
| None | (not predicted) | isinstance check fails, raises ValueError | n/a |



# Trace v1: validate_email (before running)

| Input | My prediction | What the code actually does (by reading it) | Match? |
|---|---|---|---|
| "ada@example.com" | True | passes every check, returns True | Yes |
| "ada@ example.com" | False | " " in email, returns False | Yes |
| "ada@.com" | False | domain ".com" contains a dot, ending "com" is valid, returns True | No: SILENT WRONG ANSWER. Accepts an email with no domain name before the dot. Not covered by my spec or tests (spec gap). |

**Discrepancy vs spec:** the code adds `ending.isalpha()` (ending must be letters only). This rule is not in my spec; the LLM added it without being asked.



# Trace v1: sanitise_phone (before running)

| Input | My prediction | What the code actually does (by reading it) | Match? |
|---|---|---|---|
| "07700 900123" | raises ValueError / adds +44 (unsure) | digits "07700900123", leading 0 swapped for 44, returns "+447700900123" | No: I was unsure; the code converts it correctly |
| "+447700900123" | returns "+447700900123" | already 44 + 10 digits, returns "+447700900123" | Yes |
| "+44 (0)7700 900123" | returns "+447700900123" (removes the 0) | digits "4407700900123" = 13 digits; the (0) is kept; raises ValueError | No: valid UK format rejected. My spec does not cover "(0)" (spec gap). |



# Trace v1: process_contact (before running)

| Input | My prediction | What the code actually does (by reading it) | Match? |
|---|---|---|---|
| valid Ada record | (not predicted) | returns {"first": "Ada", "last": "Lovelace", "email_ok": True, "phone": "+447700900123"} | n/a |
| name "Cher" | raises ValueError | parse_name fails, re-raised as ValueError("name: ...") | Yes |
| Does it change the input dict? | Yes | No: only reads raw_record[...], never assigns to it; returns a new dict | No: I expected mutation (like lab Draft A), but the "Do NOT change the input dict" constraint worked |
| None instead of a dict | (not predicted) | `"name" not in None` raises TypeError, not ValueError | Spec gap: spec does not say what happens with a non-dict |


# Test run v1 (27 Nov 2026)

Result: 31 passed, 0 failed.

All tests pass, but hand tracing found two problems the tests did not catch, because neither case was in my spec:
1. validate_email("ada@.com") returns True: silent wrong answer (no domain name before the dot).
2. sanitise_phone("+44 (0)7700 900123") raises ValueError: a valid UK format is rejected because the (0) is kept, giving 13 digits.

Conclusion: the gaps are in my specification, not just the code. Next: update the spec first, then the tests, then the prompt.