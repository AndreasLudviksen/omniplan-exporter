import sqlite3
import sys

def generate_report(note_string, db_name='omniplan.db'):
    """
    Generates a report for the task that matches the given note string, including nested sub-tasks.

    Args:
        note_string (str): The string to search for in the Notes column.
        db_name (str): The name of the SQLite database file.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT UID, Name FROM tasks WHERE LOWER(Notes) LIKE LOWER(?)
            ''', (f"%{note_string}%",))
            parent_task = cursor.fetchone()

            if parent_task:
                parent_uid, parent_name = parent_task
                report_filename = f"{note_string.upper()}-extended.txt"
                with open(report_filename, 'w') as report_file:
                    report_file.write(f"Description for {note_string.upper()}\n\n")
                    report_file.write(f"DoD:\n")
                    write_subtasks(cursor, report_file, parent_uid, 1)

                print(f"Report generated: {report_filename}")
            else:
                print(f"No task found with notes containing: {note_string}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

def write_subtasks(cursor, report_file, parent_uid, level):
    cursor.execute('''
        SELECT UID, Name, Milestone, OutlineLevel, Start FROM tasks WHERE ParentUID = ?
    ''', (parent_uid,))
    sub_tasks = cursor.fetchall()

    if sub_tasks:
        milestones = []
        for sub_task in sub_tasks:
            uid, name, milestone, outline_level, start = sub_task
            if milestone:
                start_date = start.split("T")[0] if start else "N/A"
                milestones.append((name, start_date, outline_level))
            else:
                report_file.write(f"{'  ' * (outline_level - 1)}oppgave: {name}\n")
                write_subtasks(cursor, report_file, uid, level + 1)

        for milestone, start_date, outline_level in milestones:
            report_file.write(f"{'  ' * (outline_level - 1)}Milepæl: {milestone} - Deadline: {start_date}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_description_for_task_with_assignments.py <note_string>")
    else:
        note_string = sys.argv[1]
        generate_report(note_string)
