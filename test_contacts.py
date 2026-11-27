import pytest
from contacts import parse_name, validate_email, sanitise_phone, process_contact


# ---------- parse_name ----------

def test_parse_name_normal():
    assert parse_name("Ada Lovelace") == {"first": "Ada", "last": "Lovelace"}


def test_parse_name_single_name_rejected():
    with pytest.raises(ValueError):
        parse_name("Cher")

def test_parse_name_empty_rejected():
    with pytest.raises(ValueError):
        parse_name("")

def test_parse_name_only_spaces_rejected():
    with pytest.raises(ValueError):
        parse_name("   ")

def test_parse_name_none_rejected():
    with pytest.raises(ValueError):
        parse_name(None)

def test_parse_name_three_words():
    assert parse_name("Mary Ann Evans") == {"first": "Mary", "last": "Ann Evans"}

def test_parse_name_extra_spaces_lowercase():
    assert parse_name("  ada   lovelace  ") == {"first": "Ada", "last": "Lovelace"}


# ---------- validate_email ----------

def test_validate_email_normal():
    assert validate_email("ada@example.com") is True


def test_validate_email_no_at_rejected():
    assert validate_email("adaexample.com") is False

def test_validate_email_one_letter_ending():
    assert validate_email("ada@example.c") is False

def test_validate_email_internal_space():
    assert validate_email("ada@ example.com") is False  

def test_validate_email_double_at():
    assert validate_email("ada@@example.com") is False 

def test_validate_email_no_dot():
    assert validate_email("ada@example") is False 

def test_validate_email_none():
    assert validate_email(None) is False

def test_validate_email_surrounding_spaces():
    assert validate_email(" ada@example.com ") is False 

def test_validate_email_no_domain_name():
    assert validate_email("ada@.com") is False


# ---------- sanitise_phone ----------

def test_sanitise_phone_normal():
    assert sanitise_phone("07700 900123") == "+447700900123"

def test_sanitise_phone_already_plus44():
    assert sanitise_phone("+447700900123") == "+447700900123"

def test_sanitise_phone_starts_44():
    assert sanitise_phone("447700900123") == "+447700900123"

def test_sanitise_phone_brackets_dashes():
    assert sanitise_phone("(07700) 900-123") == "+447700900123"

def test_sanitise_phone_plus44_with_zero_in_brackets():
    assert sanitise_phone("+44 (0)7700 900123") == "+447700900123"

def test_sanitise_phone_no_digits_rejected():
    with pytest.raises(ValueError):
        sanitise_phone("no digits here")

def test_sanitise_phone_empty_rejected():
    with pytest.raises(ValueError):
        sanitise_phone("")

def test_sanitise_phone_none_rejected():
    with pytest.raises(ValueError):
        sanitise_phone(None)

def test_sanitise_phone_too_short_rejected():
    with pytest.raises(ValueError):
        sanitise_phone("0770")

def test_sanitise_phone_too_long_rejected():
    with pytest.raises(ValueError):
        sanitise_phone("077009001234567")

def test_sanitise_phone_non_uk_rejected():
    with pytest.raises(ValueError):
        sanitise_phone("+1 555 123 4567")

# ---------- process_contact ----------
def test_process_contact_normal():
    raw = {"name": "Ada Lovelace", "email": "ada@example.com", "phone": "07700 900123"}
    assert process_contact(raw) == {
        "first": "Ada",
        "last": "Lovelace",
        "email_ok": True,
        "phone": "+447700900123",
    }


def test_process_contact_does_not_change_input():
    raw = {"name": "Ada Lovelace", "email": "ada@example.com", "phone": "07700 900123"}
    original = dict(raw)
    process_contact(raw)
    assert raw == original


def test_process_contact_bad_name_rejected():
    raw = {"name": "Cher", "email": "ada@example.com", "phone": "07700 900123"}
    with pytest.raises(ValueError):
        process_contact(raw)

def test_process_contact_bad_phone_rejected():
    raw = {"name": "Ada Lovelace", "email": "ada@example.com", "phone": "0770"}
    with pytest.raises(ValueError):
        process_contact(raw)

def test_process_contact_missing_phone_rejected():
    raw = {"name": "Ada Lovelace", "email": "ada@example.com"}
    with pytest.raises(ValueError):
        process_contact(raw)



def test_process_contact_bad_email_gives_false():
    raw = {"name": "Ada Lovelace", "email": "not-an-email", "phone": "07700 900123"}
    result = process_contact(raw)
    assert result["email_ok"] is False