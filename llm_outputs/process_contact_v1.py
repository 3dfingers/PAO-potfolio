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