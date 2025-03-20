import re

def validate_date_format(date_str):
    """
    Validates if the given date string is in the format 'YYYY-MM-DD'.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(date_pattern, date_str))

def validate_iso8601_duration(duration):
    """
    Validates if the given duration string is in ISO 8601 format.

    Args:
        duration (str): The duration string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    iso8601_pattern = r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$"
    return bool(re.match(iso8601_pattern, duration))
