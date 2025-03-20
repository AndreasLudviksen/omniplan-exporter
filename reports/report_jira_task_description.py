import sys
import os
import sqlite3
from datetime import datetime

from omniplan_exporter.db import operations

def generate_report(epos, db_path, output_dir='resources/reports'):
    """
    Generates a report for the task that matches the given note string, including nested sub-tasks.
    """
    try:
        conn = sqlite3.connect(db_path)
        parent_task = operations.get_parent_task(conn, epos)
        if parent_task:
            parent_uid, parent_name, parent_note, start_date, finish_date, _, _, _ = parent_task

            operations.create_report_directory()
            report_filename = os.path.join(output_dir, f"jira-task-description-{epos.upper()}.txt")
            with open(report_filename, 'w') as report_file:
                operations.write_report_header(report_file, epos, parent_name, parent_note)
                operations.write_subtasks(conn.cursor(), report_file, parent_uid, 1)
                
                report_file.write(f"\nDates:\nStart Date: {start_date}\nFinish Date: {finish_date}\n")
                
                # Add the generation date at the end of the report
                report_file.write(f"\nDenne beskrivelsen ble generert {datetime.now().date()}")

            print(f"Report generated: {report_filename}")
        else:
            print(f"No task found with epos number: {epos}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), '../resources/omniplan.db')  # Update the path to the database
    output_dir = 'resources/reports'
    if len(sys.argv) < 2:
        print("Usage: python report_jira_task_description.py <epos> [output_dir]")
    else:
        epos = sys.argv[1]
        if len(sys.argv) > 2:
            output_dir = sys.argv[2]
        generate_report(epos, db_path, output_dir)