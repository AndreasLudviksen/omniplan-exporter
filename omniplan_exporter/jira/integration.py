import requests
import logging
from omniplan_exporter.utils import validation
from omniplan_exporter.config import TARGET_START_FIELD, TARGET_END_FIELD, JIRA_BASE_URL

logger = logging.getLogger(__name__)


def fetch_jira_issue(issue_key, jira_base_url, bearer_token):
    """
    Fetches details of a Jira issue.

    Args:
        issue_key (str): The Jira issue key (e.g., "PROJECT-123").
        jira_base_url (str): The base URL of the Jira instance.
        bearer_token (str): The bearer token for authentication.

    Returns:
        dict: The JSON response containing issue details, or None if the request fails.
    """
    url = f"{jira_base_url}/rest/api/2/issue/{issue_key}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Jira issue {issue_key}: {e}")
        return None


def update_jira_issue(
    issue_key,
    jira_base_url=JIRA_BASE_URL,
    bearer_token=None,
    original_estimate=None,
    target_start=None,
    target_end=None,
    worklog_duration=None,
):
    """
    Updates the originalEstimate field, Target Start, and Target End fields of an
    existing Jira issue,
    empties its worklog, and adds a new worklog entry.

    Args:
        issue_key (str): The Jira issue key (e.g., "PROJECT-123").
        jira_base_url (str): The base URL of the Jira instance.
        bearer_token (str): The bearer token for authentication.
        original_estimate (str): The new value for the
        originalEstimate field (e.g., "5d").
        target_start (str, optional): The new value for the
        Target Start field (format: "YYYY-MM-DD").
        target_end (str, optional): The new value for the
        Target End field (format: "YYYY-MM-DD").
        worklog_duration (str, optional): The duration for the
        new worklog entry (ISO 8601 format, e.g., "PT1H").
    """
    if not issue_key.startswith("MUP-"):
        logger.error(f"Issue key {issue_key} does not belong to the 'MUP' project.")
        return None

    # Validate date format for target_start and target_end
    if target_start and not validation.validate_date_format(target_start):
        logger.error(
            f"Target Start value '{target_start}' is not in the format 'YYYY-MM-DD'."
        )
        return None
    if target_end and not validation.validate_date_format(target_end):
        logger.error(
            f"Target End value '{target_end}' is not in the format 'YYYY-MM-DD'."
        )
        return None

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Empty the worklog
    try:
        worklog_url = f"{jira_base_url}/rest/api/2/issue/{issue_key}/worklog"
        worklog_response = requests.get(worklog_url, headers=headers)
        worklog_response.raise_for_status()
        worklogs = worklog_response.json().get("worklogs", [])

        for worklog in worklogs:
            delete_url = f"{worklog_url}/{worklog['id']}"
            delete_response = requests.delete(delete_url, headers=headers)
            if delete_response.status_code == 204:
                logger.info(f"Deleted worklog {worklog['id']} for issue {issue_key}.")
            else:
                logger.warning(
                    f"Failed to delete worklog {worklog['id']} for issue {issue_key}: "
                    f"{delete_response.text}"
                )
    except requests.RequestException as e:
        logger.error(f"Failed to empty worklog for Jira issue {issue_key}: {e}")
        return None

    # Update fields
    try:
        url = f"{jira_base_url}/rest/api/2/issue/{issue_key}"
        update_data = {"fields": {}}

        if original_estimate:
            update_data["fields"]["timetracking"] = {
                "originalEstimate": original_estimate,
                "remainingEstimate": original_estimate,
            }
        if target_start:
            update_data["fields"][TARGET_START_FIELD] = target_start
        if target_end:
            update_data["fields"][TARGET_END_FIELD] = target_end

        response = requests.put(url, headers=headers, json=update_data)
        logger.info(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Content: {response.text}")

        # Handle 204 No Content explicitly
        if response.status_code == 204:
            logger.info(
                f"Successfully updated Jira issue {issue_key}. No content returned."
            )
        else:
            response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to update Jira issue {issue_key}: {e}")
        return None

    # Add a new worklog entry
    if worklog_duration and worklog_duration != "0h 0m":
        try:
            worklog_data = {"timeSpent": worklog_duration, "comment": "Added via API"}
            add_worklog_response = requests.post(
                worklog_url, headers=headers, json=worklog_data
            )
            if add_worklog_response.status_code == 201:
                logger.info(
                    f"Successfully added worklog entry with duration "
                    f"{worklog_duration} for issue {issue_key}."
                )
            else:
                logger.warning(
                    f"Failed to add worklog entry for issue {issue_key}: "
                    f"{add_worklog_response.text}"
                )
        except requests.RequestException as e:
            logger.error(
                "Failed to add worklog entry for Jira issue %s: %s",
                issue_key,
                e,
            )
            return None

    return {
        "status": "success",
        "message": "Issue updated, worklog emptied, and new worklog added",
    }
