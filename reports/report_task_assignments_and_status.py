import sys
import os
import sqlite3
import logging
from datetime import datetime

from omniplan_exporter.db import operations

logger = logging.getLogger(__name__)


def generate_assignments_report(conn, epos, output_dir="resources/reports"):
    parent_task = operations.get_parent_task(conn, epos)
    if not parent_task:
        logger.error(f"No task found for epos: {epos}")
        return

    operations.create_report_directory()
    report_filename = os.path.join(
        output_dir, f"task-assignments-and-status-{epos.upper()}.md"
    )
    with open(report_filename, "w") as report_file:
        (
            task_uid,
            task_name,
            task_notes,
            task_start,
            task_finish,
            task_percent_complete,
            task_work,
            task_epos,
        ) = parent_task
        jira_link = operations.get_jira_link(conn, task_uid)
        report_file.write(f"# Assignments and status for {jira_link}\n\n")
        report_file.write("| Jira | Task Name | Effort | Complete | Start | Finish |\n")
        report_file.write("|------|-----------|--------|----------|-------|--------|\n")
        report_file.write(
            f"| {jira_link} | {task_name} | "
            f"{operations.convert_to_work_days(task_work)}d | "
            f"{task_percent_complete or 0}% | {task_start} | {task_finish} |\n\n"
        )
        report_file.write("## Sub-tasks\n\n")
        sub_tasks = operations.get_sub_tasks_and_assignments(conn, task_uid)
        report_file.write(
            "| Jira | Task Name | Effort | Complete | Start | Finish | Assignments |\n"
        )
        report_file.write(
            "|------|-----------|--------|----------|-------|--------|-------------|\n"
        )
        for sub_task in sub_tasks:
            (
                sub_task_uid,
                name,
                work_days,
                percent_complete,
                start_date,
                finish_date,
            ) = sub_task
            jira_link = operations.get_jira_link(conn, sub_task_uid)
            report_file.write(
                f"| {jira_link} | {name} | {work_days}d | "
                f"{percent_complete or 0}% | {start_date} | {finish_date} | "
            )
            # Fetch assignments for the sub-task
            assignments = operations.get_assignments_by_uid(conn, sub_task_uid)
            if assignments:
                assignment_list = ", ".join(
                    [
                        f"{resource_name} ({units * 100:.1f}%)"
                        for resource_name, units in assignments
                    ]
                )
                report_file.write(f"{assignment_list}")
            else:
                report_file.write("N/A")
            report_file.write(" |\n")
        report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}\n")

    logger.info(f"Report generated: {report_filename}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )
    if len(sys.argv) < 2:
        logger.error(
            "Usage: python report_task_assignments_and_status.py <epos> [output_dir]"
        )
        sys.exit(1)

    epos = sys.argv[1]
    output_dir = "resources/reports"
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    db_path = os.path.join(os.path.dirname(__file__), "../resources/omniplan.db")
    conn = sqlite3.connect(db_path)
    generate_assignments_report(conn, epos, output_dir)
    conn.close()
