# app/modules/onboarding/models/validators.py

def not_blank(value: str) -> str:
    """
    Validates that the given string value is not blank (empty or only whitespace).

    Args:
        value (str): The string value to validate.

    Returns:
        str: The stripped, non-blank string value.

    Raises:
        ValueError: If the input value is blank or contains only whitespace.
    """
    value = (value or "").strip()
    if not value:
        raise ValueError("This field is required.")
    return value

def valid_email(value: str) -> str:
    """
    Validates that the provided value is a properly formatted email address.

    Args:
        value (str): The email address to validate.

    Returns:
        str: The validated and stripped email address.

    Raises:
        ValueError: If the value does not contain both "@" and "." characters, indicating an invalid email address.
    """
    value = (value or "").strip()
    if "@" not in value or "." not in value:
        raise ValueError("Enter a valid email address.")
    return value

def matches_pattern(value: str, pattern: str, error_msg: str) -> str:
    """
    Validates that the given string value matches the specified regular expression pattern.

    Args:
        value (str): The input string to validate.
        pattern (str): The regular expression pattern to match against.
        error_msg (str): The error message to raise if the value does not match the pattern.

    Returns:
        str: The stripped input value if it matches the pattern.

    Raises:
        ValueError: If the input value does not match the pattern.
    """
    import re
    if not re.match(pattern, value.strip()):
        raise ValueError(error_msg)
    return value.strip()
