import sqlite3
import logging
import os
import isodate
from datetime import datetime


def create_connection(db_name):
    return sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)


def insert_tasks_into_db(conn, tasks):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_tasks")
    create_tasks_table(cursor)
    cursor.executemany(
        (
            """
            INSERT INTO omniplan_tasks (
                UID, ID, Name, OutlineLevel, Type, Priority, Start, Finish, Duration,
                Work, ActualWork, RemainingWork, Summary, Milestone, Notes, ParentUID,
                PercentComplete
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        ),
        tasks,
    )
    logging.info(f"Inserted {len(tasks)} task records into the database.")


def insert_resources_into_db(conn, resources):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_resources")
    create_resources_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_resources (
            UID, ID, Name, Type, MaxUnits, CalendarUID, GroupName
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        resources,
    )
    logging.info(f"Inserted {len(resources)} resource records into the database.")


def insert_assignments_into_db(conn, assignments):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_assignments")
    create_assignments_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_assignments (
            UID, TaskUID, ResourceUID, Milestone, PercentWorkComplete, Units, Work,
            ActualWork, RemainingWork, Start, Finish
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        assignments,
    )
    logging.info(f"Inserted {len(assignments)} assignment records into the database.")


def insert_calendars_into_db(conn, calendars):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_calendars")
    create_calendars_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_calendars (
            UID, Name, IsBaseCalendar, BaseCalendarUID
        ) VALUES (?, ?, ?, ?)
        """,
        calendars,
    )
    logging.info(f"Inserted {len(calendars)} calendar records into the database.")


def insert_calendar_weekdays_into_db(conn, calendar_weekdays):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_calendar_weekdays")
    create_calendar_weekdays_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_calendar_weekdays (
            CalendarUID, DayType, DayWorking, FromTime, ToTime
        ) VALUES (?, ?, ?, ?, ?)
        """,
        calendar_weekdays,
    )
    logging.info(
        "Inserted %d calendar weekday records into the database.",
        len(calendar_weekdays),
    )


def insert_calendar_exceptions_into_db(conn, calendar_exceptions):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_calendar_exceptions")
    create_calendar_exceptions_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_calendar_exceptions (
            CalendarUID, ExceptionUID, Name, FromDate, ToDate
        ) VALUES (?, ?, ?, ?, ?)
        """,
        calendar_exceptions,
    )
    logging.info(
        f"Inserted {len(calendar_exceptions)} calendar exception records "
        f"into the database."
    )


def insert_extended_attributes_into_db(conn, extended_attributes):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_task_extended_attributes")
    create_extended_attributes_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_task_extended_attributes (TaskUID, FieldID, Value)
        VALUES (?, ?, ?)
        """,
        extended_attributes,
    )
    logging.info(
        f"Inserted {len(extended_attributes)} extended attribute records "
        f"into the database."
    )


def insert_predecessor_links_into_db(conn, predecessor_links):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS omniplan_predecessor_links")
    create_predecessor_links_table(cursor)
    cursor.executemany(
        """
        INSERT INTO omniplan_predecessor_links (TaskUID, PredecessorUID, Type)
        VALUES (?, ?, ?)
        """,
        predecessor_links,
    )
    conn.commit()


def create_tasks_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_tasks (
            UID INTEGER PRIMARY KEY,
            ID INTEGER,
            Name TEXT,
            OutlineLevel INTEGER,
            Type INTEGER,
            Priority INTEGER,
            Start DATETIME,
            Finish DATETIME,
            Duration TEXT,
            Work TEXT,
            ActualWork TEXT,
            RemainingWork TEXT,
            Summary INTEGER,
            Milestone INTEGER,
            Notes TEXT,
            ParentUID INTEGER,
            PercentComplete REAL,
            FOREIGN KEY (ParentUID) REFERENCES omniplan_tasks(UID)
        )
        """
    )


def create_resources_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_resources (
            UID INTEGER PRIMARY KEY,
            ID INTEGER,
            Name TEXT,
            Type INTEGER,
            MaxUnits REAL,
            CalendarUID INTEGER,
            GroupName TEXT
        )
        """
    )


def create_assignments_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_assignments (
            UID INTEGER PRIMARY KEY,
            TaskUID INTEGER,
            ResourceUID INTEGER,
            Milestone INTEGER,
            PercentWorkComplete REAL,
            Units REAL,
            Work TEXT,
            ActualWork TEXT,
            RemainingWork TEXT,
            Start DATETIME,
            Finish DATETIME,
            FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID),
            FOREIGN KEY (ResourceUID) REFERENCES omniplan_resources(UID)
        )
        """
    )


def create_calendars_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_calendars (
            UID INTEGER PRIMARY KEY,
            Name TEXT,
            IsBaseCalendar INTEGER,
            BaseCalendarUID INTEGER
        )
        """
    )


def create_calendar_weekdays_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_calendar_weekdays (
            CalendarUID INTEGER,
            DayType INTEGER,
            DayWorking TEXT,
            FromTime TEXT,
            ToTime TEXT,
            FOREIGN KEY (CalendarUID) REFERENCES omniplan_calendars(UID)
        )
        """
    )


def create_calendar_exceptions_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_calendar_exceptions (
            CalendarUID INTEGER,
            ExceptionUID INTEGER,
            Name TEXT,
            FromDate TEXT,
            ToDate TEXT,
            FOREIGN KEY (CalendarUID) REFERENCES omniplan_calendars(UID)
        )
        """
    )


def create_extended_attributes_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_task_extended_attributes (
            TaskUID INTEGER,
            FieldID INTEGER,
            Value TEXT,
            FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID)
        )
        """
    )


def create_predecessor_links_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS omniplan_predecessor_links (
            TaskUID INTEGER,
            PredecessorUID INTEGER,
            Type INTEGER,
            FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID),
            FOREIGN KEY (PredecessorUID) REFERENCES omniplan_tasks(UID)
        )
        """
    )


def get_parent_task(conn, epos):
    """
    Retrieves the parent task based on the epos parameter from the
    omniplan_task_extended_attributes table.

    Args:
        epos (str): The epos number to search for.
        conn (sqlite3.Connection): The SQLite database connection.

    Returns:
        tuple: The parent task UID, name, notes, start date, finish date,
        percent complete, work, and epos value, or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.UID, t.Name, t.Notes, t.Start, t.Finish, t.PercentComplete, t.Work,
        tea.Value
        FROM omniplan_tasks t
        JOIN omniplan_task_extended_attributes tea ON t.UID = tea.TaskUID
        WHERE tea.FieldID = 188743731 AND LOWER(tea.Value) = LOWER(?)
        """,
        (epos,),
    )
    result = cursor.fetchone()
    if result:
        uid, name, notes, start, finish, percent_complete, work, epos_value = result
        start_date = datetime.fromisoformat(start).date() if start else "N/A"
        finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"
        return (
            uid,
            name,
            notes,
            start_date,
            finish_date,
            percent_complete,
            work,
            epos_value,
        )
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
    cursor.execute(
        """
        SELECT UID, Name, Milestone, OutlineLevel, Start
        FROM omniplan_tasks
        WHERE ParentUID = ?
        """,
        (parent_uid,),
    )
    sub_tasks = cursor.fetchall()

    # Retrieve predecessor links
    cursor.execute(
        """
        SELECT PredecessorUID, Type FROM omniplan_predecessor_links WHERE TaskUID = ?
        """,
        (parent_uid,),
    )
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
    report_file.write("DoD:\n")


def write_subtasks(cursor, report_file, parent_uid, level):
    """
    Writes the sub-tasks to the report file.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        report_file (file object): The file object to write to.
        parent_uid (int): The UID of the parent task.
        level (int): The current outline level.
    """
    cursor.execute(
        """
        SELECT UID, Name, Milestone, OutlineLevel, Start FROM omniplan_tasks WHERE
        ParentUID = ?
        """,
        (parent_uid,),
    )
    sub_tasks = cursor.fetchall()

    if sub_tasks:
        milestones = []
        for sub_task in sub_tasks:
            uid, name, milestone, outline_level, start = sub_task
            if milestone:
                # Only use the date part of start_date
                try:
                    start_date = (
                        datetime.fromisoformat(start).date() if start else "N/A"
                    )
                except ValueError:
                    start_date = "N/A"
                milestones.append((name, start_date, outline_level))
            else:
                report_file.write(f"{'    ' * (outline_level - 1)}- oppgave: {name}\n")
                write_subtasks(cursor, report_file, uid, level + 1)

        for milestone, start_date, outline_level in milestones:
            report_file.write(
                f"{'    ' * (outline_level - 1)}* Milepæl: {milestone} - "
                f"Deadline: {start_date}\n"
            )


def create_report_directory():
    """
    Creates the directory for storing generated reports.
    """
    os.makedirs("resources/reports", exist_ok=True)


def get_tasks_by_outline(conn, outline_level, milestone=0):
    """
    Retrieves tasks with the specified OutlineLevel and optional Milestone.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        outline_level (int): The outline level of the tasks.
        milestone (int, optional): The milestone status of the tasks. Defaults to 0.

    Returns:
        list: A list of tuples containing the task UID, name, finish date, start date,
        work, and actual work.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT UID, Name, Finish, Start, Work, ActualWork
        FROM omniplan_tasks
        WHERE OutlineLevel=? AND Milestone=?
        """,
        (outline_level, milestone),
    )
    return cursor.fetchall()


logger = logging.getLogger(__name__)


def get_task_dependencies(conn, milestone_id, dependency_type):
    cursor = conn.cursor()
    try:
        if dependency_type == "predecessor":
            query = """
                SELECT t.Name
                FROM omniplan_tasks t
                JOIN omniplan_predecessor_links d ON t.UID = d.PredecessorUID
                WHERE d.TaskUID = ?
            """
        elif dependency_type == "successor":
            query = """
                SELECT t.Name
                FROM omniplan_tasks t
                JOIN omniplan_predecessor_links d ON t.UID = d.TaskUID
                WHERE d.PredecessorUID = ?
            """
        else:
            logger.warning(
                "Invalid dependency_type. Must be 'predecessor' or 'successor'."
            )

        cursor.execute(query, (milestone_id,))
        dependencies = cursor.fetchall()
        return [{"Name": dep[0]} for dep in dependencies]

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
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
    cursor.execute(
        """
        SELECT UID, Name, Work, PercentComplete, Start, Finish, Summary
        FROM omniplan_tasks
        WHERE ParentUID = ?
        """,
        (task_uid,),
    )
    sub_tasks = cursor.fetchall()

    all_sub_tasks = []
    for sub_task in sub_tasks:
        uid, name, work, percent_complete, start, finish, summary = sub_task
        if not summary:
            work_days = convert_to_work_days(work)
            start_date = datetime.fromisoformat(start).date() if start else "N/A"
            finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"
            all_sub_tasks.append(
                (uid, name, work_days, percent_complete, start_date, finish_date)
            )
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
        return round(duration_timedelta.total_seconds() / (7.5 * 3600))
    except (isodate.ISO8601Error, TypeError):
        return "N/A"


def get_jira_number(conn, task_uid):
    """
    Retrieves the Jira number for a given task UID.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (int): The UID of the task.

    Returns:
        str: The Jira number or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT Value
        FROM omniplan_task_extended_attributes
        WHERE TaskUID = ? AND FieldID = 188743731
        """,
        (task_uid,),
    )
    result = cursor.fetchone()
    return result[0] if result else None


def get_jira_link(conn, task_uid):
    """
    Constructs the Jira link for a given task UID using the Jira number.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (int): The UID of the task.

    Returns:
        str: The Jira link or None if the Jira number is not found.
    """
    jira_number = get_jira_number(conn, task_uid)
    if jira_number:
        return f"[{jira_number}](https://jira.sits.no/browse/{jira_number})"
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
    cursor.execute(
        """
        SELECT a.ResourceUID, a.Units, r.Name
        FROM omniplan_assignments a
        JOIN omniplan_resources r ON a.ResourceUID = r.UID
        WHERE a.TaskUID = ?
        """,
        (task_uid,),
    )
    assignments = cursor.fetchall()
    return [
        (resource_name, units) for resource_uid, units, resource_name in assignments
    ]
