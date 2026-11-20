# Unit 1 Specifications

Author:
Role(s) this unit: Solo (Architect, Builder, Integrator, Tester)
Date written (before any code was generated):

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
| `""` (empty) | raises ValueError | No name given; consistent with rejecting incomplete names || `"   "` (only spaces) | returns {"first": "", "last": ""} | Treat as blank |
| `"   "` (only spaces) | raises ValueError | Strip spaces first; nothing left means no name, so reject || `"  ada   lovelace  "` (extra spaces, lowercase) | | |
| `"Mary Ann Evans"` (3+ parts) | returns {"first": "Mary", "last": "Ann Evans"} | First word is first name; the rest is kept as surname so multi-word surnames (e.g. "van der Berg") are not lost |
| `"  ada   lovelace  "` (extra spaces, lowercase) | returns {"first": "Ada", "last": "Lovelace"} | Extra spaces removed and names capitalised for consistent records. Known trade-off: names like "McDonald" become "Mcdonald" |1.
| `None` / not a string | raises ValueError | Treated as no valid name; consistent with empty input |

---

## 2. validate_email

**Signature:** `validate_email(email: str) -> bool`

**Returns:**

**Raises:** (does it ever raise? decide and state it)

**Decisions on open cases:**
| Input | Decision | Why |
|---|---|---|
| `"ada@example.com"` | | |
| `"ada@example.c"` | | |
| `"ada@ example.com"` (internal space) | | |
| `"adaexample.com"` (no @) | | |
| `"ada@@example.com"` | | |
| `"ada@example"` (no dot in domain) | | |
| `None` / not a string | | |
| `" ada@example.com "` (surrounding spaces) | | |

**Negative examples (must NOT …), at least two:**
1.
2.

---

## 3. sanitise_phone

**Signature:** `sanitise_phone(raw: str) -> str`

**Returns (exact output format):**

**Raises (exception type and when):**
-

**Decisions on open cases:**
| Input | Decision | Why |
|---|---|---|
| `"07700 900123"` | | |
| `"+447700900123"` (already +44) | | |
| `"447700900123"` | | |
| `"(07700) 900-123"` | | |
| `"no digits here"` | | |
| `""` | | |
| `None` | | |
| Too few / too many digits | | |

**Negative examples (must NOT …), at least two:**
1.
2.

---

## 4. process_contact (pipeline)

**Signature:** `process_contact(raw_record: dict) -> dict`

**Input keys expected:**

**Output keys (exact names):**

**Behaviour when a component raises:**

**Behaviour when an input key is missing:**

**Negative examples (must NOT …), at least two:**
1. Must NOT silently accept a one-word name: "Cher" must raise ValueError, not return a result
2. Must NOT use a bare `except:` that hides errors; errors must be raised with a clear message

## Change log
Record every change to this spec after testing, with the date and the reason.

| Date | Change | Reason (which test or finding caused it) |
|---|---|---|