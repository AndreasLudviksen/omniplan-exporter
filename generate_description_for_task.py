import sqlite3
import sys

def generate_report(note_string, db_name='omniplan.db'):
    """
    Generates a report for the task that matches the given note string.

    Args:
        note_string (str): The string to search for in the Notes column.
        db_name (str): The name of the SQLite database file.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT UID FROM tasks WHERE LOWER(Notes) LIKE LOWER(?)
            ''', (f"%{note_string}%",))
            parent_task = cursor.fetchone()

            if parent_task:
                parent_uid = parent_task[0]
                cursor.execute('''
                    SELECT Name, Milestone, Start FROM tasks WHERE ParentUID = ?
                ''', (parent_uid,))
                sub_tasks = cursor.fetchall()

                report_filename = f"{note_string.upper()}.txt"
                with open(report_filename, 'w') as report_file:
                    report_file.write(f"Description for {note_string.upper()}\n\n")
                    report_file.write(f"DoD:\n")
                    milestones = []
                    for sub_task in sub_tasks:
                        name, milestone, start = sub_task
                        if milestone:
                            start_date = start.split("T")[0] if start else "N/A"
                            milestones.append((name, start_date))
                        else:
                            report_file.write(f"* {name}\n")

                    if milestones:
                        report_file.write(f"\nMilepæler:\n")
                        for milestone, start_date in milestones:
                            report_file.write(f"* {milestone} - {start_date}\n")

                print(f"Report generated: {report_filename}")
            else:
                print(f"No task found with notes containing: {note_string}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_report.py <note_string>")
    else:
        note_string = sys.argv[1]
        generate_report(note_string)
