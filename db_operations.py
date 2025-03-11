import sqlite3
import logging

def insert_tasks_into_db(tasks, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS tasks')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
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
                FOREIGN KEY (ParentUID) REFERENCES tasks(UID)
            )
        ''')
        cursor.executemany('''
            INSERT INTO tasks (
                UID, ID, Name, OutlineLevel, Type, Priority, Start, Finish, Duration, Work, ActualWork, RemainingWork, Summary, Milestone, Notes, ParentUID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tasks)
        logging.info(f"Inserted {len(tasks)} task records into the database.")

def insert_resources_into_db(resources, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS resources')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
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
            INSERT INTO resources (
                UID, ID, Name, Type, MaxUnits, CalendarUID, GroupName
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', resources)
        logging.info(f"Inserted {len(resources)} resource records into the database.")

def insert_assignments_into_db(assignments, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS assignments')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
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
                FOREIGN KEY (TaskUID) REFERENCES tasks(UID),
                FOREIGN KEY (ResourceUID) REFERENCES resources(UID)
            )
        ''')
        cursor.executemany('''
            INSERT INTO assignments (
                UID, TaskUID, ResourceUID, Milestone, PercentWorkComplete, Units, Work, ActualWork, RemainingWork, Start, Finish
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', assignments)
        logging.info(f"Inserted {len(assignments)} assignment records into the database.")

def insert_calendars_into_db(calendars, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS calendars')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendars (
                UID INTEGER PRIMARY KEY,
                Name TEXT,
                IsBaseCalendar INTEGER,
                BaseCalendarUID INTEGER
            )
        ''')
        cursor.executemany('''
            INSERT INTO calendars (
                UID, Name, IsBaseCalendar, BaseCalendarUID
            ) VALUES (?, ?, ?, ?)
        ''', calendars)
        logging.info(f"Inserted {len(calendars)} calendar records into the database.")

def insert_calendar_weekdays_into_db(calendar_weekdays, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS calendar_weekdays')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_weekdays (
                CalendarUID INTEGER,
                DayType INTEGER,
                DayWorking TEXT,
                FromTime TEXT,
                ToTime TEXT,
                FOREIGN KEY (CalendarUID) REFERENCES calendars(UID)
            )
        ''')
        cursor.executemany('''
            INSERT INTO calendar_weekdays (
                CalendarUID, DayType, DayWorking, FromTime, ToTime
            ) VALUES (?, ?, ?, ?, ?)
        ''', calendar_weekdays)
        logging.info(f"Inserted {len(calendar_weekdays)} calendar weekday records into the database.")

def insert_calendar_exceptions_into_db(calendar_exceptions, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS calendar_exceptions')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_exceptions (
                CalendarUID INTEGER,
                ExceptionUID INTEGER,
                Name TEXT,
                FromDate TEXT,
                ToDate TEXT,
                FOREIGN KEY (CalendarUID) REFERENCES calendars(UID)
            )
        ''')
        cursor.executemany('''
            INSERT INTO calendar_exceptions (
                CalendarUID, ExceptionUID, Name, FromDate, ToDate
            ) VALUES (?, ?, ?, ?, ?)
        ''', calendar_exceptions)
        logging.info(f"Inserted {len(calendar_exceptions)} calendar exception records into the database.")

def insert_extended_attributes_into_db(extended_attributes, db_name):
    """
    Inserts extended attributes into the database.

    Args:
        extended_attributes (list): A list of tuples containing extended attribute data.
        db_name (str): The name of the SQLite database file.
    """
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS task_extended_attributes')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_extended_attributes (
                TaskUID INTEGER,
                FieldID INTEGER,
                Value TEXT,
                FOREIGN KEY (TaskUID) REFERENCES tasks(UID)
            )
        ''')
        cursor.executemany('''
            INSERT INTO task_extended_attributes (TaskUID, FieldID, Value)
            VALUES (?, ?, ?)
        ''', extended_attributes)
        logging.info(f"Inserted {len(extended_attributes)} extended attribute records into the database.")
