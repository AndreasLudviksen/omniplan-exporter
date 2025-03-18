import sys
import os
import sqlite3
from datetime import datetime

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_read_operations import get_parent_task, get_sub_tasks_and_assignments, get_jira_link, get_assignments, create_report_directory, convert_to_work_days

def generate_assignments_report(conn, epos, output_dir='resources/reports'):
    parent_task = get_parent_task(conn, epos)
    if not parent_task:
        print(f"No task found for epos: {epos}")
        return

    create_report_directory()
    report_filename = os.path.join(output_dir, f"task-assignments-and-status-{epos.upper()}.md")
    with open(report_filename, 'w') as report_file:
        task_uid, task_name, task_notes, task_start, task_finish, task_percent_complete, task_work, task_epos = parent_task
        jira_link = get_jira_link(conn, task_uid)
        report_file.write(f"# Assignments and status for {jira_link}\n\n")
        report_file.write("| Jira | Task Name | Effort | Complete | Start | Finish |\n")
        report_file.write("|------|-----------|--------|----------|-------|--------|\n")
        report_file.write(f"| {jira_link} | {task_name} | {convert_to_work_days(task_work)}d | {task_percent_complete or 0}% | {task_start} | {task_finish} |\n\n")
        
        report_file.write(f"## Sub-tasks\n\n")
        sub_tasks = get_sub_tasks_and_assignments(conn, task_uid)
        report_file.write("| Jira | Task Name | Effort | Complete | Start | Finish | Assignments |\n")
        report_file.write("|------|-----------|--------|----------|-------|--------|-------------|\n")
        for sub_task in sub_tasks:
            sub_task_uid, name, work_days, percent_complete, start_date, finish_date = sub_task
            jira_link = get_jira_link(conn, sub_task_uid)
            report_file.write(f"| {jira_link} | {name} | {work_days}d | {percent_complete or 0}% | {start_date} | {finish_date} | ")

            # Fetch assignments for the sub-task
            assignments = get_assignments(conn, sub_task_uid)
            if assignments:
                assignment_list = ", ".join([f"{resource_name} ({units * 100:.1f}%)" for resource_name, units in assignments])
                report_file.write(f"{assignment_list}")
            else:
                report_file.write("N/A")
            report_file.write(" |\n")

        report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}\n")

    print(f"Report generated: {report_filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python report_task_assignments_and_status.py <epos> [output_dir]")
        sys.exit(1)

    epos = sys.argv[1]
    output_dir = 'resources/reports'
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    db_path = os.path.join(os.path.dirname(__file__), '../resources/omniplan.db')
    conn = sqlite3.connect(db_path)
    generate_assignments_report(conn, epos, output_dir)
    conn.close()