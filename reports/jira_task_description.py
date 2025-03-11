import sys
import os
import sqlite3
from datetime import datetime
from report_utils import get_parent_task, write_report_header, write_subtasks, create_report_directory

def generate_report(epos, db_path):
    """
    Generates a report for the task that matches the given note string, including nested sub-tasks.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            parent_task = get_parent_task(epos, db_path)
            if parent_task:
                parent_uid, parent_name, parent_note, start_date, finish_date = parent_task

                create_report_directory()
                report_filename = os.path.join('resources/reports', f"{epos.upper()}.txt")
                with open(report_filename, 'w') as report_file:
                    write_report_header(report_file, epos, parent_name, parent_note)
                    write_subtasks(cursor, report_file, parent_uid, 1)
                    
                    # Add start and finish dates to the report (only date part)
                    start_date = datetime.fromisoformat(start_date).date() if start_date else "N/A"
                    finish_date = datetime.fromisoformat(finish_date).date() if finish_date else "N/A"
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
    if len(sys.argv) != 2:
        print("Usage: python generate_description_for_task_with_assignments.py <epos>")
    else:
        epos = sys.argv[1]
        generate_report(epos, db_path)
