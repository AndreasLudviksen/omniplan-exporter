import sys
import os
import sqlite3
import logging
from datetime import datetime

from omniplan_exporter.db import operations

logger = logging.getLogger(__name__)


def generate_report(jira_task, db_path, output_dir="resources/reports"):
    """
    Generates a report for the task that matches the given note string,
    including nested sub-tasks.
    """
    try:
        conn = sqlite3.connect(db_path)
        parent_task = operations.get_parent_task(conn, jira_task)
        if parent_task:
            (
                parent_uid,
                parent_name,
                parent_note,
                start_date,
                finish_date,
                _,
                _,
                _,
            ) = parent_task

            operations.create_report_directory()
            report_filename = os.path.join(
                output_dir, f"jira-task-description-{jira_task.upper()}.txt"
            )
            with open(report_filename, "w") as report_file:
                operations.write_report_header(
                    report_file, jira_task, parent_name, parent_note
                )
                operations.write_subtasks(conn.cursor(), report_file, parent_uid, 1)

                report_file.write(
                    f"\nDates:\nStart Date: {start_date}\nFinish Date: {finish_date}\n"
                )

                # Add the generation date at the end of the report
                report_file.write(
                    f"\nDenne beskrivelsen ble generert {datetime.now().date()}"
                )

            logger.info(f"Report generated: {report_filename}")
        else:
            logger.error(f"No task found with jira_task number: {jira_task}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    db_path = os.path.join(
        os.path.dirname(__file__), "../resources/omniplan.db"
    )  # Update the path to the database
    output_dir = "resources/reports"
    if len(sys.argv) < 2:
        logger.error(
            "Usage: python report_jira_task_description.py <jira_task> [output_dir]"
        )
    else:
        jira_task = sys.argv[1]
        if len(sys.argv) > 2:
            output_dir = sys.argv[2]
        generate_report(jira_task, db_path, output_dir)
