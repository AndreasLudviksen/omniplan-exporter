import sys
import os
import sqlite3
from report_utils import get_parent_task, write_report_header, write_subtasks, create_report_directory

def generate_report(note_string, db_name='../omniplan.db'):
    """
    Generates a report for the task that matches the given note string, including nested sub-tasks.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            parent_task = get_parent_task(note_string, db_name)
            if parent_task:
                parent_uid, parent_name, parent_note = parent_task

                create_report_directory()
                report_filename = os.path.join('generated-reports', f"{note_string.upper()}-extended.txt")
                with open(report_filename, 'w') as report_file:
                    write_report_header(report_file, note_string, parent_name, parent_note)
                    write_subtasks(cursor, report_file, parent_uid, 1)

                print(f"Report generated: {report_filename}")
            else:
                print(f"No task found with notes containing: {note_string}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_description_for_task_with_assignments.py <note_string>")
    else:
        note_string = sys.argv[1]
        generate_report(note_string)
