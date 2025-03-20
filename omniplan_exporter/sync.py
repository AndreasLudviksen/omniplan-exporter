import sqlite3
import argparse
from datetime import datetime
from omniplan_exporter.db import operations
from omniplan_exporter.utils.conversions import convert_duration_from_iso8601_to_jira
from omniplan_exporter.jira.integration import update_jira_issue
from omniplan_exporter.config import JIRA_BASE_URL

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

    tasks = operations.get_tasks_by_outline(conn, outline_level=2)

    tasks_with_jira = []
    for task in tasks:
        uid, name, finish_date, start_date, work, actual_work = task
        jira_number = operations.get_jira_number(conn, uid)
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
        original_estimate = convert_duration_from_iso8601_to_jira(work) if work else "0h"
        worklog_duration = convert_duration_from_iso8601_to_jira(actual_work) if actual_work else None

        # Call update_jira_issue with formatted values
        update_jira_issue(
            issue_key=jira_number,
            jira_base_url=JIRA_BASE_URL,
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
