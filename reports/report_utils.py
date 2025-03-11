import sqlite3
import os
from datetime import datetime

def get_parent_task(epos, db_path):
    """
    Retrieves the parent task based on the epos parameter from the omniplan_task_extended_attributes table.

    Args:
        epos (str): The epos number to search for.
        db_path (str): The path to the SQLite database file.

    Returns:
        tuple: The parent task UID, name, notes, start date, and finish date, or None if not found.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.UID, t.Name, t.Notes, t.Start, t.Finish, tea.Value
            FROM omniplan_tasks t
            JOIN omniplan_task_extended_attributes tea ON t.UID = tea.TaskUID
            WHERE tea.FieldID = 188743731 AND LOWER(tea.Value) = LOWER(?)
        ''', (epos,))
        result = cursor.fetchone()
        return result[:-1] if result else None

def get_sub_tasks(parent_uid, db_path):
    """
    Retrieves the sub-tasks for a given parent task UID.

    Args:
        parent_uid (int): The UID of the parent task.
        db_path (str): The path of the SQLite database file.

    Returns:
        list: A list of sub-tasks.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT UID, Name, Milestone, OutlineLevel, Start FROM omniplan_tasks WHERE ParentUID = ?
        ''', (parent_uid,))
        sub_tasks = cursor.fetchall()
        
        # Retrieve predecessor links
        cursor.execute('''
            SELECT PredecessorUID, Type FROM omniplan_predecessor_links WHERE TaskUID = ?
        ''', (parent_uid,))
        predecessor_links = cursor.fetchall()
        
        return sub_tasks, predecessor_links

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
        SELECT UID, Name, Milestone, OutlineLevel, Start FROM omniplan_tasks WHERE ParentUID = ?
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
    os.makedirs('resources/reports', exist_ok=True)

def get_tasks_by_outline(db_path, outline_level, milestone=0):
    """
    Retrieves tasks with the specified OutlineLevel and optional Milestone.

    Args:
        db_path (str): The path of the SQLite database file.
        outline_level (int): The outline level of the tasks.
        milestone (int, optional): The milestone status of the tasks. Defaults to 0.

    Returns:
        list: A list of tuples containing the task UID, name and finish date.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT UID, Name, Finish FROM omniplan_tasks WHERE OutlineLevel=? AND Milestone=?
        ''', (outline_level, milestone))
        return cursor.fetchall()

def get_task_dependencies(db_path, milestone_id, dependency_type):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"get_task_dependencies. milestone_id: {milestone_id}. dependency_type: {dependency_type}")
    try:
        if dependency_type == 'predecessor':
            query = """
                SELECT t.Name
                FROM omniplan_tasks t
                JOIN omniplan_predecessor_links d ON t.UID = d.PredecessorUID
                WHERE d.TaskUID = ?
            """
        elif dependency_type == 'successor':
            query = """
                SELECT t.Name
                FROM omniplan_tasks t
                JOIN omniplan_predecessor_links d ON t.UID = d.TaskUID
                WHERE d.PredecessorUID = ?
            """
        else:
            raise ValueError("Invalid dependency_type. Must be 'predecessor' or 'successor'.")

        print(f"query: {query}.")
        cursor.execute(query, (milestone_id,))
        dependencies = cursor.fetchall()
        return [{'Name': dep[0]} for dep in dependencies]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()
