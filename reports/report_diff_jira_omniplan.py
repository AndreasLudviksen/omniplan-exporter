import os
import sys
import sqlite3
import logging
import requests
import datetime
from dotenv import load_dotenv
from omniplan_exporter.db.operations import (
    get_parent_task,
    get_sub_tasks,
    get_jira_number,
)
from omniplan_exporter.jira.integration import fetch_jira_issue

logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()
DB_FILE_PATH = os.getenv("DB_FILE_PATH")
if not DB_FILE_PATH:
    logger.error("Environment variable DB_FILE_PATH is not set.")
    sys.exit(1)

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")


def fetch_jira_task_tree(jira_task, bearer_token):
    """
    Fetches the task tree from Jira starting from the given jira_task.

    Args:
        jira_task (str): The Jira task key.
        bearer_token (str): The bearer token for Jira API.

    Returns:
        dict: A nested dictionary representing the task tree.
    """
    # Extract the project key from the jira_task
    project_key = jira_task.split("-")[0]
    if project_key != "MUP":
        logger.error(f"Invalid project key: {project_key}. Only 'MUP' is supported.")
        sys.exit(1)

    def fetch_children(parent_key):
        # Modify the JQL query to exclude sub-tasks explicitly
        jql_query = (
            f'"Parent Link" = "{parent_key}" AND project = "{project_key}" '
            f'AND issuetype NOT IN ("Sub-task")'
        )
        url = f"{JIRA_BASE_URL}/rest/api/2/search"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }
        params = {"jql": jql_query, "fields": "key,summary,issuetype,status"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            issues = response.json().get("issues", [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch child issues for {parent_key}: {e}")
            return {}

        # Exclude subtasks by checking the "subtask" field in "issuetype"
        children = {
            f"{issue['key']} - {issue['fields']['summary']} "
            f"[Status: {issue['fields']['status']['name']}]": fetch_children(
                issue["key"]
            )
            for issue in issues
            if not issue["fields"]["issuetype"].get("subtask", False)
        }
        return children

    # Fetch the root task details
    root_issue = fetch_jira_issue(jira_task, JIRA_BASE_URL, bearer_token)
    if not root_issue:
        logger.error(f"Failed to fetch details for Jira task: {jira_task}")
        sys.exit(1)

    root_summary = root_issue.get("fields", {}).get("summary", "No Summary")
    root_status = root_issue.get("fields", {}).get("status", {}).get("name", "Unknown")
    return {
        f"{jira_task} - {root_summary} [Status: {root_status}]": fetch_children(
            jira_task
        )
    }


def fetch_omniplan_task_tree(conn, jira_task):
    """
    Fetches the task tree from OmniPlan starting from the task matching
    the given jira_task.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        jira_task (str): The Jira task key.

    Returns:
        dict: A nested dictionary representing the task tree.
    """
    parent_task = get_parent_task(conn, jira_task)
    if not parent_task:
        return {}

    def fetch_children(task_uid):
        sub_tasks, _ = get_sub_tasks(conn, task_uid)
        return {
            f"{get_jira_number(conn, sub_task[0]) or '<No Jira>'} - "
            f"{sub_task[1]} [PercentWorkComplete: {sub_task[5] or 0}%]": fetch_children(
                sub_task[0]
            )
            for sub_task in sub_tasks
        }

    jira_number = parent_task[7] or "<No Jira>"
    return {
        f"{jira_number} - {parent_task[1]} "
        f"[PercentWorkComplete: {parent_task[5] or 0}%]": fetch_children(parent_task[0])
    }


def sort_tree_by_jira_number(tree):
    """
    Sorts a nested dictionary by Jira number.

    Args:
        tree (dict): The nested dictionary to sort.

    Returns:
        dict: A sorted nested dictionary.
    """

    def extract_jira_number(key):
        # Extract Jira number or assign a high value for "<No Jira>"
        jira_number = key.split(" - ")[0]
        return (
            int(jira_number.split("-")[1])
            if jira_number != "<No Jira>"
            else float("inf")
        )

    sorted_tree = dict(
        sorted(tree.items(), key=lambda item: extract_jira_number(item[0]))
    )
    for key, value in sorted_tree.items():
        if isinstance(value, dict):
            sorted_tree[key] = sort_tree_by_jira_number(value)
    return sorted_tree


def print_tree(tree, indent=0):
    """
    Prints a nested dictionary as a readable tree structure.

    Args:
        tree (dict): The nested dictionary to print.
        indent (int): The current indentation level.
    """
    lines = []
    for key, value in tree.items():
        lines.append(" " * indent + f"- {key}")
        if isinstance(value, dict):
            lines.extend(print_tree(value, indent + 4))
    return lines


def find_diff_tree(jira_tree, omniplan_tree):
    """
    Creates a tree of tasks that are only present in one of the two trees,
    or tasks that are closed in Jira but not 100% complete in OmniPlan.

    Args:
        jira_tree (dict): The Jira task tree.
        omniplan_tree (dict): The OmniPlan task tree.

    Returns:
        dict: A nested dictionary with tasks only in one of the trees or
        mismatched statuses.
    """

    def extract_jira_number(key):
        # Extract Jira number from the key (e.g., "MUP-123 - Summary")
        return key.split(" - ")[0]

    def extract_status(key):
        # Extract status from the key (e.g., "[Status: Lukket]")
        return key.split("[Status: ")[-1].strip("]")

    def extract_percent_complete(key):
        # Extract PercentWorkComplete from the key
        # (e.g., "[PercentWorkComplete: 57.0%]")
        try:
            return float(key.split("[PercentWorkComplete: ")[-1].strip("%]"))
        except ValueError:
            logger.error(f"Failed to extract PercentWorkComplete from key: {key}")
            return 0.0

    diff_tree = {}

    jira_keys = {extract_jira_number(key): key for key in jira_tree.keys()}
    omniplan_keys = {extract_jira_number(key): key for key in omniplan_tree.keys()}

    all_jira_numbers = set(jira_keys.keys()).union(omniplan_keys.keys())

    for jira_number in all_jira_numbers:
        if jira_number in jira_keys and jira_number not in omniplan_keys:
            diff_tree[f"(Only in Jira) {jira_keys[jira_number]}"] = jira_tree[
                jira_keys[jira_number]
            ]
        elif jira_number in omniplan_keys and jira_number not in jira_keys:
            diff_tree[
                f"(Only in OmniPlan) {omniplan_keys[jira_number]}"
            ] = omniplan_tree[omniplan_keys[jira_number]]
        elif jira_number in jira_keys and jira_number in omniplan_keys:
            jira_status = extract_status(jira_keys[jira_number])
            omniplan_percent_complete = extract_percent_complete(
                omniplan_keys[jira_number]
            )

            # Check for mismatched statuses
            if jira_status == "Lukket" and omniplan_percent_complete < 100:
                diff_tree[
                    f"(Task closed in Jira) {jira_keys[jira_number]}"
                ] = omniplan_tree[omniplan_keys[jira_number]]
            elif jira_status != "Lukket" and omniplan_percent_complete == 100:
                diff_tree[
                    f"(Task closed in Omniplan) {omniplan_keys[jira_number]}"
                ] = jira_tree[jira_keys[jira_number]]

            # Recursively check for differences in nested dictionaries (skip subtasks)
            nested_diff = find_diff_tree(
                jira_tree[jira_keys[jira_number]],
                omniplan_tree[omniplan_keys[jira_number]],
            )
            if nested_diff:
                diff_tree[jira_keys[jira_number]] = nested_diff

    return diff_tree


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if len(sys.argv) < 2:
        logger.error(
            "Usage: python report_diff_jira_omniplan.py <jira_task> <bearer_token>"
        )
        sys.exit(1)

    jira_task = sys.argv[1]
    bearer_token = sys.argv[2]

    # Connect to the database
    conn = sqlite3.connect(DB_FILE_PATH)

    # Fetch task trees
    jira_tree = fetch_jira_task_tree(jira_task, bearer_token)
    omniplan_tree = fetch_omniplan_task_tree(conn, jira_task)

    # Sort task trees by Jira number
    jira_tree = sort_tree_by_jira_number(jira_tree)
    omniplan_tree = sort_tree_by_jira_number(omniplan_tree)

    # Create and print the diff tree
    diff_tree = find_diff_tree(jira_tree, omniplan_tree)

    # Prepare the output directory
    output_dir = os.path.join("resources", "reports")
    os.makedirs(output_dir, exist_ok=True)

    # Generate the output file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"report_diff_{jira_task}_{timestamp}.txt")

    # Write the output to the file
    with open(output_file, "w") as file:
        file.write("Jira Task Tree:\n")
        file.write("-" * 20 + "\n")
        for line in print_tree(jira_tree, indent=0):
            file.write(line + "\n")

        file.write("\nOmniPlan Task Tree:\n")
        file.write("-" * 20 + "\n")
        for line in print_tree(omniplan_tree, indent=0):
            file.write(line + "\n")

        file.write("\nTasks Only in One Tree:\n")
        file.write("-" * 20 + "\n")
        for line in print_tree(diff_tree, indent=0):
            file.write(line + "\n")

    logger.info(f"Report written to {output_file}")

    conn.close()
