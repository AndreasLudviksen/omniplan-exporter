import sqlite3
import logging

def create_connection(db_name):
    return sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)

def insert_tasks_into_db(conn, tasks):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_tasks')
    cursor.execute('''
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
            FOREIGN KEY (ParentUID) REFERENCES omniplan_tasks(UID)
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_tasks (
            UID, ID, Name, OutlineLevel, Type, Priority, Start, Finish, Duration, Work, ActualWork, RemainingWork, Summary, Milestone, Notes, ParentUID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tasks)
    logging.info(f"Inserted {len(tasks)} task records into the database.")

def insert_resources_into_db(conn, resources):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_resources')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omniplan_resources (
            UID INTEGER PRIMARY KEY,
            ID INTEGER,
            Name TEXT,
            Type INTEGER,
            MaxUnits REAL,
            CalendarUID INTEGER,
            GroupName TEXT
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_resources (
            UID, ID, Name, Type, MaxUnits, CalendarUID, GroupName
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', resources)
    logging.info(f"Inserted {len(resources)} resource records into the database.")

def insert_assignments_into_db(conn, assignments):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_assignments')
    cursor.execute('''
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
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_assignments (
            UID, TaskUID, ResourceUID, Milestone, PercentWorkComplete, Units, Work, ActualWork, RemainingWork, Start, Finish
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', assignments)
    logging.info(f"Inserted {len(assignments)} assignment records into the database.")

def insert_calendars_into_db(conn, calendars):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_calendars')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omniplan_calendars (
            UID INTEGER PRIMARY KEY,
            Name TEXT,
            IsBaseCalendar INTEGER,
            BaseCalendarUID INTEGER
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_calendars (
            UID, Name, IsBaseCalendar, BaseCalendarUID
        ) VALUES (?, ?, ?, ?)
    ''', calendars)
    logging.info(f"Inserted {len(calendars)} calendar records into the database.")

def insert_calendar_weekdays_into_db(conn, calendar_weekdays):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_calendar_weekdays')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omniplan_calendar_weekdays (
            CalendarUID INTEGER,
            DayType INTEGER,
            DayWorking TEXT,
            FromTime TEXT,
            ToTime TEXT,
            FOREIGN KEY (CalendarUID) REFERENCES omniplan_calendars(UID)
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_calendar_weekdays (
            CalendarUID, DayType, DayWorking, FromTime, ToTime
        ) VALUES (?, ?, ?, ?, ?)
    ''', calendar_weekdays)
    logging.info(f"Inserted {len(calendar_weekdays)} calendar weekday records into the database.")

def insert_calendar_exceptions_into_db(conn, calendar_exceptions):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_calendar_exceptions')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omniplan_calendar_exceptions (
            CalendarUID INTEGER,
            ExceptionUID INTEGER,
            Name TEXT,
            FromDate TEXT,
            ToDate TEXT,
            FOREIGN KEY (CalendarUID) REFERENCES omniplan_calendars(UID)
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_calendar_exceptions (
            CalendarUID, ExceptionUID, Name, FromDate, ToDate
        ) VALUES (?, ?, ?, ?, ?)
    ''', calendar_exceptions)
    logging.info(f"Inserted {len(calendar_exceptions)} calendar exception records into the database.")

def insert_extended_attributes_into_db(conn, extended_attributes):
    """
    Inserts extended attributes into the database.

    Args:
        extended_attributes (list): A list of tuples containing extended attribute data.
        db_name (str): The name of the SQLite database file.
    """
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_task_extended_attributes')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omniplan_task_extended_attributes (
            TaskUID INTEGER,
            FieldID INTEGER,
            Value TEXT,
            FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID)
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_task_extended_attributes (TaskUID, FieldID, Value)
        VALUES (?, ?, ?)
    ''', extended_attributes)
    logging.info(f"Inserted {len(extended_attributes)} extended attribute records into the database.")

def insert_predecessor_links_into_db(conn, predecessor_links):
    """
    Inserts predecessor links into the database.

    Args:
        predecessor_links (list): A list of predecessor link tuples.
        db_name (str): The name of the SQLite database file.
    """
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS omniplan_predecessor_links')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omniplan_predecessor_links (
            TaskUID INTEGER,
            PredecessorUID INTEGER,
            Type INTEGER,
            FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID),
            FOREIGN KEY (PredecessorUID) REFERENCES omniplan_tasks(UID)
        )
    ''')
    cursor.executemany('''
        INSERT INTO omniplan_predecessor_links (TaskUID, PredecessorUID, Type)
        VALUES (?, ?, ?)
    ''', predecessor_links)
    conn.commit()
