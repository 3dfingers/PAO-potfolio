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