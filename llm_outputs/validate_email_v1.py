def validate_email(email: str) -> bool:
    """Check whether an email address meets basic formatting requirements."""
    if not isinstance(email, str):
        return False

    if not email or " " in email or email.count("@") != 1:
        return False

    local_part, domain = email.split("@")

    if not local_part or not domain or "." not in domain:
        return False

    ending = domain.rsplit(".", 1)[-1]

    if len(ending) < 2 or not ending.isalpha():
        return False

    return True