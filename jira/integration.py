import sys
import os
import requests
import argparse
import re
import sqlite3
from datetime import datetime

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_read_operations import get_tasks_by_outline, get_jira_number  # Import get_jira_number

# Constants for custom fields
TARGET_START_FIELD = "customfield_15360"
TARGET_END_FIELD = "customfield_15361"

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
        print(f"Failed to fetch Jira issue {issue_key}: {e}")
        return None

def update_jira_issue(issue_key, jira_base_url, bearer_token, original_estimate, target_start=None, target_end=None, worklog_duration=None):
    """
    Updates the originalEstimate field, Target Start, and Target End fields of an existing Jira issue, empties its worklog, and adds a new worklog entry.

    Args:
        issue_key (str): The Jira issue key (e.g., "PROJECT-123").
        jira_base_url (str): The base URL of the Jira instance.
        bearer_token (str): The bearer token for authentication.
        original_estimate (str): The new value for the originalEstimate field (e.g., "5d").
        target_start (str, optional): The new value for the Target Start field (format: "YYYY-MM-DD").
        target_end (str, optional): The new value for the Target End field (format: "YYYY-MM-DD").
        worklog_duration (str, optional): The duration for the new worklog entry (ISO 8601 format, e.g., "PT1H").
    """
    if not issue_key.startswith("MUP-"):
        print(f"Error: Issue key {issue_key} does not belong to the 'MUP' project.")
        return None


    # Validate date format for target_start and target_end
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if target_start and not re.match(date_pattern, target_start):
        print(f"Error: Target Start value '{target_start}' is not in the format 'YYYY-MM-DD'.")
        return None
    if target_end and not re.match(date_pattern, target_end):
        print(f"Error: Target End value '{target_end}' is not in the format 'YYYY-MM-DD'.")
        return None


    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
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
                print(f"Deleted worklog {worklog['id']} for issue {issue_key}.")
            else:
                print(f"Failed to delete worklog {worklog['id']} for issue {issue_key}: {delete_response.text}")
    except requests.RequestException as e:
        print(f"Failed to empty worklog for Jira issue {issue_key}: {e}")
        return None

    # Update fields
    try:
        url = f"{jira_base_url}/rest/api/2/issue/{issue_key}"
        update_data = {
            "fields": {
                "timetracking": {
                    "originalEstimate": original_estimate,
                    "remainingEstimate": original_estimate
                }
            }
        }
        if target_start:
            update_data["fields"][TARGET_START_FIELD] = target_start
        if target_end:
            update_data["fields"][TARGET_END_FIELD] = target_end

        response = requests.put(url, headers=headers, json=update_data)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        # Handle 204 No Content explicitly
        if response.status_code == 204:
            print(f"Successfully updated Jira issue {issue_key}. No content returned.")
        else:
            response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to update Jira issue {issue_key}: {e}")
        return None

    # Add a new worklog entry
    if worklog_duration:
        try:
            worklog_data = {
                "timeSpent": worklog_duration,
                "comment": "Added via API"
            }
            add_worklog_response = requests.post(worklog_url, headers=headers, json=worklog_data)
            if add_worklog_response.status_code == 201:
                print(f"Successfully added worklog entry with duration {worklog_duration} for issue {issue_key}.")
            else:
                print(f"Failed to add worklog entry for issue {issue_key}: {add_worklog_response.text}")
        except requests.RequestException as e:
            print(f"Failed to add worklog entry for Jira issue {issue_key}: {e}")
            return None

    return {"status": "success", "message": "Issue updated, worklog emptied, and new worklog added"}

def sync_omniplan_with_jira(conn, bearer_token):
    """
    Synchronizes tasks from OmniPlan with Jira by fetching tasks with OutlineLevel=2,
    filtering out tasks without a Jira number, sorting them by Jira number, and printing their details.
    Updates all tasks in the list in Jira.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        bearer_token (str): The bearer token for Jira API authentication.
    """
    print("sync_omniplan_with_jira")

    tasks = get_tasks_by_outline(conn, outline_level=2)

    tasks_with_jira = []
    for task in tasks:
        uid, name, finish_date, start_date, work, actual_work = task
        jira_number = get_jira_number(conn, uid)
        if jira_number:
            tasks_with_jira.append((name, jira_number, start_date, finish_date, work, actual_work))

    # Sort tasks by Jira number
    tasks_with_jira.sort(key=lambda x: x[1])

    # Update all tasks in Jira
    for task in tasks_with_jira:
        name, jira_number, start_date, finish_date, work, actual_work = task
        print(f"Updating Jira issue for task: {name}, Jira Number: {jira_number}")

        # Format target_start and target_end
        target_start = datetime.fromisoformat(start_date).strftime("%Y-%m-%d") if start_date else None
        target_end = datetime.fromisoformat(finish_date).strftime("%Y-%m-%d") if finish_date else None

        # Convert work and actual_work to Jira-supported format
        def convert_to_jira_format(duration):
            match = re.match(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", duration)
            if not match:
                return None
            hours = match.group(1) or "0"
            minutes = match.group(2) or "0"
            jira_format = f"{hours}h {minutes}m".strip()
            return jira_format

        original_estimate = convert_to_jira_format(work) if work else "0h"
        worklog_duration = convert_to_jira_format(actual_work) if actual_work else None

        # Call update_jira_issue with formatted values
        jira_base_url = "https://jira.sits.no"

        update_jira_issue(
            issue_key=jira_number,
            jira_base_url=jira_base_url,
            bearer_token=bearer_token,
            original_estimate=original_estimate,
            target_start=target_start,
            target_end=target_end,
            worklog_duration=worklog_duration
        )

def main():
    """
    Main function to synchronize OmniPlan tasks with Jira.
    """
    parser = argparse.ArgumentParser(description="Synchronize OmniPlan tasks with Jira.")
    parser.add_argument("--db-path", required=True, help="Path to the SQLite database file.")
    parser.add_argument("--bearer-token", required=True, help="Bearer token for Jira API authentication.")
    args = parser.parse_args()

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(args.db_path)
        print(f"Connected to database at {args.db_path}")

        # Call the synchronization function
        sync_omniplan_with_jira(conn, args.bearer_token)
        print("Synchronization completed successfully.")
    except Exception as e:
        print(f"Failed to synchronize tasks: {e}")
    finally:
        # Ensure the database connection is closed
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()