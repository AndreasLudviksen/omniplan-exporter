import re
from omniplan_exporter.utils.validation import validate_iso8601_duration


def convert_duration_from_iso8601_to_jira(duration):
    """
    Converts an ISO 8601 duration string to Jira-supported format.

    Args:
        duration (str): The ISO 8601 duration string (e.g., "PT1H30M").

    Returns:
        str: The duration in Jira format (e.g., "1h 30m"), or None if invalid.
    """
    if not validate_iso8601_duration(duration):
        return None

    match = re.match(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", duration)
    hours = match.group(1) or "0"
    minutes = match.group(2) or "0"
    jira_format = f"{hours}h {minutes}m".strip()
    return jira_format
