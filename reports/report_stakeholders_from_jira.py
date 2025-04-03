import os
import sys
import logging
import sqlite3
from dotenv import load_dotenv  # Import dotenv to load environment variables
from omniplan_exporter.db import operations  # Import operations for fetching tasks
from omniplan_exporter.jira.integration import fetch_jira_issue
from datetime import datetime

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
DB_FILE_PATH = os.getenv("DB_FILE_PATH")  # Get DB_FILE_PATH from .env
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # Get JIRA_BASE_URL from .env


def generate_stakeholders_report(bearer_token, conn, output_dir="resources/reports"):
    """
    Generates a report containing a pivot table with "Task Name" on the Y-axis,
    "Navn" on the X-axis, and "Rolle" as the cell value.

    Args:
        bearer_token (str): The bearer token for authentication.
        conn (sqlite3.Connection): The SQLite database connection.
        output_dir (str): The directory where the report will be saved.
    """
    try:
        # Fetch tasks with outline_level=2
        tasks = operations.get_tasks_by_outline(conn, outline_level=2)

        # Filter tasks by ParentUID
        tasks = [task for task in tasks if task[-1] in (32, 261)]

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Prepare data for the pivot table
        pivot_data = {}
        all_names = set()
        task_data = []  # Collect task data with start_date for sorting

        for task in tasks:
            uid, name, _, start, _, _, parent_uid = task  # Include start field
            jira_number = operations.get_jira_number(conn, uid)
            if jira_number:
                issue_details = fetch_jira_issue(
                    jira_number, JIRA_BASE_URL, bearer_token
                )
                raw_allocation = (
                    issue_details.get("fields", {}).get("customfield_27860", "N/A")
                    if issue_details
                    else "N/A"
                )
                if raw_allocation != "N/A":
                    allocation_lines = raw_allocation.splitlines()
                    allocation_data = [
                        line.split(" - ")[:2] for line in allocation_lines
                    ]
                else:
                    allocation_data = []

                # Prefix task name with Jira issue number and make it a link
                name = f"[{jira_number} - {name}]({JIRA_BASE_URL}/browse/{jira_number})"

                # Add start date in the same cell with a line break.
                # Only include the date part.
                start_date = None
                if start:
                    start_date = start.split(" ")[0]  # Extract only the date part
                    name += f"<br>Oppstart: {start_date}"

                for navn, rolle in allocation_data:
                    all_names.add(navn)
                    if name not in pivot_data:
                        pivot_data[name] = {}
                    pivot_data[name][navn] = rolle

                # Append task data for sorting
                task_data.append((start_date, name, pivot_data[name]))

        # Sort tasks by start_date (None values will be last)
        task_data.sort(key=lambda x: (x[0] is None, x[0]))

        # Separate names with parentheses to be the first columns
        names_with_parentheses = sorted([name for name in all_names if "(" in name])
        other_names = sorted([name for name in all_names if "(" not in name])
        all_names = names_with_parentheses + other_names

        # Write report to file
        report_filename = os.path.join(output_dir, "stakeholders_report.md")
        with open(report_filename, "w") as report_file:
            report_file.write("# interessentrapport\n\n")

            # Write header row
            header_row = ["Task Name"] + all_names
            column_widths = [
                max(len(name), 12) for name in header_row
            ]  # Ensure minimum width of 12
            formatted_header = (
                "| "
                + " | ".join(
                    f"{name:<{width}}" for name, width in zip(header_row, column_widths)
                )
                + " |"
            )
            header_separator = (
                "|-" + "-|-".join("-" * width for width in column_widths) + "-|"
            )

            report_file.write(formatted_header + "\n")
            report_file.write(header_separator + "\n")

            # Write rows for each task, sorted by start_date
            for _, task_name, allocations in task_data:
                row = [allocations.get(navn, "") for navn in all_names]
                formatted_row = (
                    "| "
                    + " | ".join(
                        f"{value:<{width}}"
                        for value, width in zip([task_name] + row, column_widths)
                    )
                    + " |"
                )
                report_file.write(formatted_row + "\n")

            report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}")

        logger.info(f"Report generated: {report_filename}")

    except Exception as e:
        logger.error(f"An error occurred while generating the report: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if len(sys.argv) < 2:
        logger.error("Usage: python report_stakeholders_from_jira.py <bearer_token>")
    else:
        bearer_token = sys.argv[1]
        conn = sqlite3.connect(DB_FILE_PATH)  # Use DB_FILE_PATH from .env
        generate_stakeholders_report(bearer_token, conn)
        conn.close()
