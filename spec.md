# Unit 1 Specifications

Author:
Role(s) this unit: Solo (Architect, Builder, Integrator, Tester)
Date written (before any code was generated):

Rule: the specification is the single source of truth. If code and spec disagree, the spec wins. If reality and spec disagree, change the spec first, then the prompt, then the code.

---

## 1. parse_name

**Signature:** `parse_name(full_name: str) -> dict`

**Returns:**

**Raises (exception type and when):**
-

**Decisions on open cases:**
| Input | Decision (return value or exception) | Why |
|---|---|---|
| `"Ada Lovelace"` | | |
| `"Cher"` (single name) | | |
| `""` (empty) | | |
| `"   "` (only spaces) | | |
| `"Mary Ann Evans"` (3+ parts) | | |
| `"  ada   lovelace  "` (extra spaces, lowercase) | | |
| `None` / not a string | | |

**Negative examples (must NOT …), at least two:**
1.
2.

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
1. (hint: think about the input dict)
2.

---

## Change log
Record every change to this spec after testing, with the date and the reason.

| Date | Change | Reason (which test or finding caused it) |
|---|---|---|