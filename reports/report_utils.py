import sqlite3
import os
from datetime import datetime

def get_parent_task(note_string, db_name):
    """
    Retrieves the parent task that matches the given note string.

    Args:
        note_string (str): The string to search for in the Notes column.
        db_name (str): The name of the SQLite database file.

    Returns:
        tuple: The parent task UID and name, or None if not found.
    """
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT UID, Name, Notes FROM tasks WHERE LOWER(Notes) LIKE LOWER(?)
        ''', (f"%{note_string}%",))
        return cursor.fetchone()

def get_sub_tasks(parent_uid, db_name):
    """
    Retrieves the sub-tasks for a given parent task UID.

    Args:
        parent_uid (int): The UID of the parent task.
        db_name (str): The name of the SQLite database file.

    Returns:
        list: A list of sub-tasks.
    """
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT UID, Name, Milestone, OutlineLevel, Start FROM tasks WHERE ParentUID = ?
        ''', (parent_uid,))
        return cursor.fetchall()

def write_report_header(report_file, note_string, task_name, parent_note):
    """
    Writes the header for the report.

    Args:
        report_file (file object): The file object to write to.
        note_string (str): The note string used for the report.
    """
    # Skip the first line of parent_note
    parent_note_lines = parent_note.split('\n')
    parent_note = '\n'.join(parent_note_lines[1:])

    report_file.write(f"Description for {note_string.upper()} - {task_name}\n\n")
    report_file.write(f"Scope: \n{parent_note}\n\n")
    report_file.write(f"DoD:\n")

def write_subtasks(cursor, report_file, parent_uid, level):
    """
    Writes the sub-tasks to the report file.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        report_file (file object): The file object to write to.
        parent_uid (int): The UID of the parent task.
        level (int): The current outline level.
    """
    cursor.execute('''
        SELECT UID, Name, Milestone, OutlineLevel, Start FROM tasks WHERE ParentUID = ?
    ''', (parent_uid,))
    sub_tasks = cursor.fetchall()

    if sub_tasks:
        milestones = []
        for sub_task in sub_tasks:
            uid, name, milestone, outline_level, start = sub_task
            if milestone:
                # Only use the date part of start_date
                try:
                    start_date = datetime.fromisoformat(start).date() if start else "N/A"
                except ValueError:
                    start_date = "N/A"
                milestones.append((name, start_date, outline_level))
            else:
                report_file.write(f"{'    ' * (outline_level - 1)}- oppgave: {name}\n")
                write_subtasks(cursor, report_file, uid, level + 1)

        for milestone, start_date, outline_level in milestones:
            report_file.write(f"{'    ' * (outline_level - 1)}* Milepæl: {milestone} - Deadline: {start_date}\n")

def create_report_directory():
    """
    Creates the directory for storing generated reports.
    """
    os.makedirs('generated-reports', exist_ok=True)
