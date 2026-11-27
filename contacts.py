def parse_name(full_name: str) -> dict:
    """Split a full name into capitalised first and last names."""
    if not isinstance(full_name, str):
        raise ValueError("Name must be a string.")

    parts = full_name.split()

    if len(parts) < 2:
        raise ValueError("Full name must contain at least two words.")

    return {
        "first": parts[0].capitalize(),
        "last": " ".join(parts[1:]).title()
    }

def validate_email(email: str) -> bool:
    """Check whether an email address has a basic valid format."""
    if not isinstance(email, str):
        return False

    if not email or " " in email or email.count("@") != 1:
        return False

    local, domain = email.split("@")

    if not local or not domain or "." not in domain:
        return False

    if domain.startswith(".") or domain.endswith("."):
        return False

    if len(domain.rsplit(".", 1)[1]) < 2:
        return False

    return True

def sanitise_phone(raw: str) -> str:
    """Clean and validate a UK phone number into +44 format."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Phone number must be a non-empty string.")

    digits = "".join(char for char in raw if char.isdigit())

    if not digits:
        raise ValueError("Phone number must contain digits.")

    if digits.startswith("440"):
        digits = "44" + digits[3:]
    elif digits.startswith("0"):
        digits = "44" + digits[1:]
    elif digits.startswith("44"):
        pass
    elif raw.lstrip().startswith("+44"):
        pass
    else:
        raise ValueError("Phone number must be a UK number starting with 0 or 44.")

    if len(digits) != 12 or not digits.startswith("44"):
        raise ValueError("UK phone number must contain exactly 10 digits after 44.")

    return "+" + digits


def process_contact(raw_record: dict) -> dict:
    """Clean and validate a contact record without modifying the input."""
    required_fields = ("name", "email", "phone")

    for field in required_fields:
        if field not in raw_record:
            raise ValueError(f"missing required field: {field}")

    try:
        name_parts = parse_name(raw_record["name"])
    except ValueError as error:
        raise ValueError(f"name: {error}") from error

    email_ok = validate_email(raw_record["email"])

    try:
        phone = sanitise_phone(raw_record["phone"])
    except ValueError as error:
        raise ValueError(f"phone: {error}") from error

    return {
        "first": name_parts["first"],
        "last": name_parts["last"],
        "email_ok": email_ok,
        "phone": phone
    }
