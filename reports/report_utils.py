import sqlite3
import os
from datetime import datetime

def get_parent_task(epos, db_name):
    """
    Retrieves the parent task based on the epos parameter from the task_extended_attributes table.

    Args:
        epos (str): The epos number to search for.
        db_name (str): The name of the SQLite database file.

    Returns:
        tuple: The parent task UID, name, notes, start date, and finish date, or None if not found.
    """
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.UID, t.Name, t.Notes, t.Start, t.Finish, tea.Value
            FROM tasks t
            JOIN task_extended_attributes tea ON t.UID = tea.TaskUID
            WHERE tea.FieldID = 188743731 AND LOWER(tea.Value) = LOWER(?)
        ''', (epos,))
        result = cursor.fetchone()
        return result[:-1] if result else None

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

def write_report_header(report_file, epos, task_name, parent_note):
    """
    Writes the header for the report.

    Args:
        report_file (file object): The file object to write to.
        epos (str): The note string used for the report.
    """

    report_file.write(f"Description for {epos.upper()} - {task_name}\n\n")
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

def get_tasks_by_outline(db_name, outline_level, milestone=0):
    """
    Retrieves tasks with the specified OutlineLevel and optional Milestone.

    Args:
        db_name (str): The name of the SQLite database file.
        outline_level (int): The outline level of the tasks.
        milestone (int, optional): The milestone status of the tasks. Defaults to 0.

    Returns:
        list: A list of tuples containing the task name and finish date.
    """
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Name, Finish FROM tasks WHERE OutlineLevel=? AND Milestone=?
        ''', (outline_level, milestone))
        return cursor.fetchall()
