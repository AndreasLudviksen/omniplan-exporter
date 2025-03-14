import sys
import os
import sqlite3
from report_utils import create_report_directory, get_parent_task, get_assignments_for_task_and_subtasks
from datetime import datetime, timedelta
import isodate

def generate_assignments_report(conn, epos):
    parent_task = get_parent_task(conn, epos)
    if not parent_task:
        print(f"No task found for epos: {epos}")
        return

    task_uid, task_name, _, start, finish, percent_complete, work, parent_value = parent_task
    assignments = get_assignments_for_task_and_subtasks(conn, task_uid)

    create_report_directory()
    report_filename = os.path.join('resources/reports', f"task-assignments-and-status-{epos.upper()}.md")
    with open(report_filename, 'w') as report_file:
        report_file.write(f"# Assignments Report for {epos}\n\n")
        report_file.write("\n")
        report_file.write("| Jira | Task Name | Complete | Effort |\n")
        report_file.write("| --- | --- | --- | --- |\n")
        
        # Write parent task
        parent_jira_link = f"https://jira.sits.no/browse/{parent_value}" if parent_value != 'None' else "N/A"
        parent_work_days = convert_to_work_days(work)
        report_file.write(f"| {parent_jira_link} | {task_name} | {percent_complete}% | {parent_work_days} d |\n")
        
        report_file.write("\n")
        report_file.write("| Jira | Task Name | Resource | Assignment |Effort | Complete | Start | Finish |\n")
        report_file.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
        
        for assignment in assignments:
            task_uid, task_name, resource_name, percent_work_complete, units, start, finish, value, work, actual_work, remaining_work = assignment
            start_date = start.split('T')[0] if start else "N/A"
            finish_date = finish.split('T')[0] if finish else "N/A"
            jira_link = f"https://jira.sits.no/browse/{value}" if value != 'None' else "N/A"
            percent_work_complete = percent_work_complete if percent_work_complete is not None else 0
            work_days = convert_to_work_days(work)
            report_file.write(f"| {jira_link} | {task_name} | {resource_name} | {units:.2f} | {work_days} d | {percent_work_complete}% | {start_date} | {finish_date} |\n")

        report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}")

    print(f"Report generated: {report_filename}")

def convert_to_work_days(duration):
    if not duration:
        return "N/A"
    try:
        duration_timedelta = isodate.parse_duration(duration)
        work_days = duration_timedelta.total_seconds() / (7.5 * 3600)
        return round(work_days)
    except (isodate.ISO8601Error, TypeError):
        return "N/A"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assignments.py <epos>")
        sys.exit(1)

    epos = sys.argv[1]
    db_path = os.path.join(os.path.dirname(__file__), '../resources/omniplan.db')
    conn = sqlite3.connect(db_path)
    generate_assignments_report(conn, epos)
    conn.close()
