import sqlite3
import os
from datetime import datetime

def get_parent_task(conn, epos):
    """
    Retrieves the parent task based on the epos parameter from the omniplan_task_extended_attributes table.

    Args:
        epos (str): The epos number to search for.
        conn (sqlite3.Connection): The SQLite database connection.

    Returns:
        tuple: The parent task UID, name, notes, start date, finish date, percent complete, work, and epos value, or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.UID, t.Name, t.Notes, t.Start, t.Finish, t.PercentComplete, t.Work, tea.Value
        FROM omniplan_tasks t
        JOIN omniplan_task_extended_attributes tea ON t.UID = tea.TaskUID
        WHERE tea.FieldID = 188743731 AND LOWER(tea.Value) = LOWER(?)
    ''', (epos,))
    result = cursor.fetchone()
    return result if result else None

def get_sub_tasks(conn, parent_uid):
    """
    Retrieves the sub-tasks for a given parent task UID.

    Args:
        parent_uid (int): The UID of the parent task.
        conn (sqlite3.Connection): The SQLite database connection.

    Returns:
        list: A list of sub-tasks.
    """
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

def get_tasks_by_outline(conn, outline_level, milestone=0):
    """
    Retrieves tasks with the specified OutlineLevel and optional Milestone.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        outline_level (int): The outline level of the tasks.
        milestone (int, optional): The milestone status of the tasks. Defaults to 0.

    Returns:
        list: A list of tuples containing the task UID, name and finish date.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT UID, Name, Finish FROM omniplan_tasks WHERE OutlineLevel=? AND Milestone=?
    ''', (outline_level, milestone))
    return cursor.fetchall()

def get_task_dependencies(conn, milestone_id, dependency_type):
    cursor = conn.cursor()
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

        cursor.execute(query, (milestone_id,))
        dependencies = cursor.fetchall()
        return [{'Name': dep[0]} for dep in dependencies]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def get_assignments_for_task_and_subtasks(conn, task_uid):
    """
    Retrieves assignments for a task and its subtasks.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (int): The UID of the task.

    Returns:
        list: A list of assignments.
    """
    cursor = conn.cursor()
    cursor.execute('''
        WITH RECURSIVE sub_tasks(UID, Name) AS (
            SELECT UID, Name FROM omniplan_tasks WHERE UID = ?
            UNION ALL
            SELECT t.UID, t.Name FROM omniplan_tasks t
            INNER JOIN sub_tasks st ON t.ParentUID = st.UID
        )
        SELECT a.TaskUID, t.Name, r.Name, a.PercentWorkComplete, a.Units, a.Start, a.Finish, 
               COALESCE(tea.Value, 'None') AS Value, a.Work, a.ActualWork, a.RemainingWork
        FROM omniplan_assignments a
        INNER JOIN sub_tasks t ON a.TaskUID = t.UID
        INNER JOIN omniplan_resources r ON a.ResourceUID = r.UID
        LEFT JOIN omniplan_task_extended_attributes tea ON t.UID = tea.TaskUID AND tea.FieldID = 188743731
    ''', (task_uid,))
    return cursor.fetchall()
