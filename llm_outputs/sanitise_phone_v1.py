def sanitise_phone(raw: str) -> str:
    """Clean and validate a UK phone number into +44 format."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Phone number must be a non-empty string.")

    digits = "".join(char for char in raw if char.isdigit())

    if not digits:
        raise ValueError("Phone number must contain digits.")

    if raw.strip().startswith("+"):
        if not raw.strip().startswith("+44") or not digits.startswith("44"):
            raise ValueError("Only UK phone numbers are accepted.")
    elif not (digits.startswith("0") or digits.startswith("44")):
        raise ValueError("Phone number must start with 0, 44 or +44.")

    if digits.startswith("0"):
        digits = "44" + digits[1:]

    if not digits.startswith("44") or len(digits) != 12:
        raise ValueError("UK phone number must contain exactly 10 digits after 44.")

    return "+" + digits