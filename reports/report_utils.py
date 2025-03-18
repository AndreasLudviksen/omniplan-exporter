import sqlite3
import os
import isodate
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
    if result:
        uid, name, notes, start, finish, percent_complete, work, epos_value = result
        start_date = datetime.fromisoformat(start).date() if start else "N/A"
        finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"
        return uid, name, notes, start_date, finish_date, percent_complete, work, epos_value
    return None

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

def get_sub_tasks_and_assignments(conn, task_uid):
    """
    Retrieves sub-tasks and assignments for the parent-task.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (int): The UID of the parent-task.

    Returns:
        list: A list of sub-tasks and assignments.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT UID, Name, Work, PercentComplete, Start, Finish, Summary
        FROM omniplan_tasks
        WHERE ParentUID = ?
    ''', (task_uid,))
    sub_tasks = cursor.fetchall()

    all_sub_tasks = []
    for sub_task in sub_tasks:
        uid, name, work, percent_complete, start, finish, summary = sub_task
        if not summary:
            work_days = convert_to_work_days(work)
            start_date = datetime.fromisoformat(start).date() if start else "N/A"
            finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"
            all_sub_tasks.append((uid, name, work_days, percent_complete, start_date, finish_date))
        all_sub_tasks.extend(get_sub_tasks_and_assignments(conn, uid))

    return all_sub_tasks

def convert_to_work_days(duration):
    """
    Converts duration to number of 7.5 hours working days.

    Args:
        duration (str): The duration string.

    Returns:
        int: The number of working days.
    """
    if not duration:
        return "N/A"
    try:
        duration_timedelta = isodate.parse_duration(duration)
        work_days = duration_timedelta.total_seconds() / (7.5 * 3600)
        return round(work_days)
    except (isodate.ISO8601Error, TypeError):
        return "N/A"

def get_jira_link(conn, task_uid):
    """
    Retrieves the Jira link for a given task UID.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (int): The UID of the task.

    Returns:
        str: The Jira link or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Value
        FROM omniplan_task_extended_attributes
        WHERE TaskUID = ? AND FieldID = 188743731
    ''', (task_uid,))
    result = cursor.fetchone()
    if result:
        jira = result[0]
        return f"[{jira}](https://jira.sits.no/browse/{jira})"
    return None

def get_assignments(conn, task_uid):
    """
    Fetches assignments for a given task UID.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (int): The UID of the task.

    Returns:
        list: A list of tuples containing the resource name and units.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.ResourceUID, a.Units, r.Name
        FROM omniplan_assignments a
        JOIN omniplan_resources r ON a.ResourceUID = r.UID
        WHERE a.TaskUID = ?
    ''', (task_uid,))
    assignments = cursor.fetchall()
    return [(resource_name, units) for resource_uid, units, resource_name in assignments]
