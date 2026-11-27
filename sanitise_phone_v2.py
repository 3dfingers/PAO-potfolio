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