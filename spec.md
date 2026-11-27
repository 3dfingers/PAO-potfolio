# Unit 1 Specifications

Author: Ndubuisi Samuel

Role(s) this unit: Solo (Architect, Builder, Integrator, Tester)

Date written (before any code was generated): 27 Nov 2026

Rule: the specification is the single source of truth. If code and spec disagree, the spec wins. If reality and spec disagree, change the spec first, then the prompt, then the code.

---

## 1. parse_name

**Signature:** `parse_name(full_name: str) -> dict`

**Returns:** a new dict {"first": str, "last": str}, with extra spaces removed and each name capitalised. First word = first name; everything after = last name.

**Raises (exception type and when):**
- ValueError if the input is not a string, is empty, is only spaces, or has fewer than two words

**Decisions on open cases:**

| Input | Decision (return value or exception) | Why |
|---|---|---|
| `"Ada Lovelace"` | returns {"first": "Ada", "last": "Lovelace"} | Normal two-part name |
| `"Cher"` (single name) | raises ValueError | Incomplete names should be flagged, not silently accepted |
| `""` (empty) | raises ValueError | No name given; consistent with rejecting incomplete names |
| `"   "` (only spaces) | raises ValueError | Strip spaces first; nothing left means no name, so reject |
| `"Mary Ann Evans"` (3+ parts) | returns {"first": "Mary", "last": "Ann Evans"} | First word is first name; the rest is kept as surname so multi-word surnames (e.g. "van der Berg") are not lost |
| `"  ada   lovelace  "` (extra spaces, lowercase) | returns {"first": "Ada", "last": "Lovelace"} | Extra spaces removed and names capitalised for consistent records. Known trade-off: names like "McDonald" become "Mcdonald" |
| `None` / not a string | raises ValueError | Treated as no valid name; consistent with empty input |

**Negative examples (must NOT …):**
1. Must NOT silently accept a one-word name: "Cher" must raise ValueError, not return a result
2. Must NOT use a bare `except:` that hides errors; errors must be raised with a clear message

---

## 2. validate_email

**Signature:** `validate_email(email: str) -> bool`

**Returns:** True if the email is valid, False otherwise.

**Raises:** Never raises. Any invalid input, including None or a non-string, returns False.

**Decisions on open cases:**

| Input | Decision | Why |
|---|---|---|
| `"ada@example.com"` | returns True | Normal valid email |
| `"ada@example.c"` | returns False | The ending after the last dot must be at least 2 letters (e.g. .uk, .com) |
| `"ada@ example.com"` (internal space) | returns False | Valid emails cannot contain spaces |
| `"adaexample.com"` (no @) | returns False | Every email must contain an @ |
| `"ada@@example.com"` | returns False | Exactly one @ allowed |
| `"ada@example"` (no dot in domain) | returns False | The part after @ must contain a dot |
| `None` / not a string | returns False | Never raises; not text means not a valid email |
| `" ada@example.com "` (surrounding spaces) | returns False | Any space anywhere makes the email invalid; consistent with the internal-space rule |
| `"ada@.com"` (no name before the dot) | returns False | The part after @ must have a name before the dot, not just ".com" |

**Negative examples (must NOT …), at least two:**
1. Must NOT accept an email containing a space anywhere (e.g. "ada@ example.com" or " ada@example.com " must return False)
2. Must NOT accept more than one @ (e.g. "ada@@example.com" must return False)

## 3. sanitise_phone

**Signature:** `sanitise_phone(raw: str) -> str`

**Returns (exact output format):** a string in the format "+44" followed by the number without its leading 0, e.g. "+447700900123"

**Raises (exception type and when):**
- ValueError if the input is None, not a string, empty, contains no digits, does not start with 0, 44 or +44 (i.e. is not a UK number), or does not have exactly 10 digits after +44
**Decisions on open cases:**

| Input | Decision | Why |
|---|---|---|
| `"07700 900123"` | returns "+447700900123" | Spaces removed; leading 0 replaced with +44 |
| `"+447700900123"` (already +44) | returns "+447700900123" | Already in the right format; left unchanged |
| `"447700900123"` | returns "+447700900123" | Starts with 44, so only the + is added |
| `"(07700) 900-123"` | returns "+447700900123" | Brackets, spaces and dashes removed before converting |
| `"no digits here"` | raises ValueError | No phone number to clean; refuse rather than return something wrong |
| `""` | raises ValueError | Empty input means no phone number |
| `None` | raises ValueError | Not a string; consistent with parse_name being strict |
| Too few / too many digits (e.g. "0770", "077009001234567") | raises ValueError | A UK number must have exactly 10 digits after +44; anything else is likely a typo |

| `"+44 (0)7700 900123"` | returns "+447700900123" | Common UK way of writing numbers; a 0 directly after the 44 is removed |
**Negative examples (must NOT …), at least two:**
1. Must NOT add a second +44 to a number that already starts with +44 (must never produce "+44447700900123")
2. Must NOT accept non-UK numbers (e.g. "+1 555 123 4567" must raise ValueError)

---

## 4. process_contact (pipeline)

**Signature:** `process_contact(raw_record: dict) -> dict`

**Input keys expected:**

**Output keys (exact names):** "first", "last", "email_ok", "phone" (returned as a NEW dict)

**Behaviour when a component raises:** Raises ValueError naming the field that failed (e.g. "name: ..." or "phone: ..."). The whole record is refused. Note: validate_email never raises, so an invalid email does not stop the record; it just gives email_ok = False.

**Behaviour when an input key is missing:**

**Negative examples (must NOT …), at least two:**
1. Must NOT change the input dict: it must return a NEW dict and leave the original record unchanged
2. Must NOT use a bare `except:` to hide errors; failures must raise ValueError naming the field

---

## Change log

Record every change to this spec after testing, with the date and the reason.

| Date | Change | Reason (which test or finding caused it) |
|---|---|---|
| 27 Nov 2026 | Added rule: domain must have a name before the dot ("ada@.com" is False) | Hand trace of v1 code showed "ada@.com" returned True; my spec did not cover this case |
| 27 Nov 2026 | Added rule: a 0 directly after 44 (e.g. "+44 (0)7700 900123") is removed | Hand trace of v1 code showed this real UK format was rejected (13 digits); my spec did not cover it |