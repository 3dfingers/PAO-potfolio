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