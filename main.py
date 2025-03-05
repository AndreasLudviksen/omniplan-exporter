import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register adapter and converter for datetime
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("DATETIME", lambda val: datetime.fromisoformat(val.decode("utf-8")))

def process_xml(file_path, db_name):
    """
    Processes an XML file and extracts various elements to insert into a database.

    Args:
        file_path (str): The path to the XML file to be processed.
        db_name (str): The name of the SQLite database file.

    Raises:
        ET.ParseError: If there is an error parsing the XML file.
        sqlite3.Error: If there is a database error.

    The function performs the following steps:
        1. Parses the XML file.
        2. Extracts tasks and inserts them into the database.
        3. Extracts resources and inserts them into the database.
        4. Extracts assignments and inserts them into the database.
        5. Extracts calendars and inserts them into the database.
        6. Extracts calendar weekdays and inserts them into the database.
        7. Extracts calendar exceptions and inserts them into the database.
    """
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract and insert tasks
        tasks = extract_tasks(root)
        insert_tasks_into_db(tasks, db_name)

        # Extract and insert resources
        resources = extract_resources(root)
        insert_resources_into_db(resources, db_name)

        # Extract and insert assignments
        assignments = extract_assignments(root)
        insert_assignments_into_db(assignments, db_name)

        # Extract and insert calendars
        calendars = extract_calendars(root)
        insert_calendars_into_db(calendars, db_name)

        # Extract and insert calendar weekdays
        calendar_weekdays = extract_calendar_weekdays(root)
        insert_calendar_weekdays_into_db(calendar_weekdays, db_name)

        # Extract and insert calendar exceptions
        calendar_exceptions = extract_calendar_exceptions(root)
        insert_calendar_exceptions_into_db(calendar_exceptions, db_name)

    except ET.ParseError as e:
        logging.error(f"Error parsing XML: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

def extract_tasks(root):
    tasks = []
    seen_uids = set()
    for task in root.findall('./Tasks/Task'):
        uid = task.find('UID').text if task.find('UID') is not None else None
        if uid in seen_uids:
            logging.error(f"Detected duplicate task uid: {uid}")
            continue
        seen_uids.add(uid)

        task_id = task.find('ID').text if task.find('ID') is not None else None
        name = task.find('Name').text if task.find('Name') is not None else None
        task_type = task.find('Type').text if task.find('Type') is not None else None
        priority = task.find('Priority').text if task.find('Priority') is not None else None

        start_str = task.find('Start').text if task.find('Start') is not None else None
        finish_str = task.find('Finish').text if task.find('Finish') is not None else None
        start = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S") if start_str else None
        finish = datetime.strptime(finish_str, "%Y-%m-%dT%H:%M:%S") if finish_str else None

        duration = task.find('Duration').text if task.find('Duration') is not None else None
        work = task.find('Work').text if task.find('Work') is not None else None
        actual_work = task.find('ActualWork').text if task.find('ActualWork') is not None else None
        remaining_work = task.find('RemainingWork').text if task.find('RemainingWork') is not None else None
        summary = int(task.find('Summary').text) if task.find('Summary') is not None else None
        milestone = int(task.find('Milestone').text) if task.find('Milestone') is not None else None
        notes = task.find('Notes').text if task.find('Notes') is not None else None
        outline_level = int(task.find('OutlineLevel').text) if task.find('OutlineLevel') is not None else None

        #logging.info(f"Extracted task: {name}, start: {start}")
        tasks.append((uid, task_id, name, task_type, priority, start, finish, duration, work, actual_work, remaining_work, summary, milestone, notes, outline_level))

    return tasks

def extract_resources(root):
    resources = []
    for resource in root.findall('./Resources/Resource'):
        uid = resource.find('UID').text if resource.find('UID') is not None else None
        resource_id = resource.find('ID').text if resource.find('ID') is not None else None
        name = resource.find('Name').text if resource.find('Name') is not None else None
        resource_type = resource.find('Type').text if resource.find('Type') is not None else None
        max_units = resource.find('MaxUnits').text if resource.find('MaxUnits') is not None else None
        calendar_uid = resource.find('CalendarUID').text if resource.find('CalendarUID') is not None else None
        group = resource.find('Group').text if resource.find('Group') is not None else None

        #logging.info(f"Extracted resource: {name}, group: {group}")
        resources.append((uid, resource_id, name, resource_type, max_units, calendar_uid, group))

    return resources

def extract_assignments(root):
    assignments = []
    for assignment in root.findall('./Assignments/Assignment'):
        uid = assignment.find('UID').text if assignment.find('UID') is not None else None
        task_uid = assignment.find('TaskUID').text if assignment.find('TaskUID') is not None else None
        resource_uid = assignment.find('ResourceUID').text if assignment.find('ResourceUID') is not None else None
        milestone = assignment.find('Milestone').text if assignment.find('Milestone') is not None else None
        percent_work_complete = assignment.find('PercentWorkComplete').text if assignment.find('PercentWorkComplete') is not None else None
        units = assignment.find('Units').text if assignment.find('Units') is not None else None
        work = assignment.find('Work').text if assignment.find('Work') is not None else None
        actual_work = assignment.find('ActualWork').text if assignment.find('ActualWork') is not None else None
        remaining_work = assignment.find('RemainingWork').text if assignment.find('RemainingWork') is not None else None
        start = assignment.find('Start').text if assignment.find('Start') is not None else None
        finish = assignment.find('Finish').text if assignment.find('Finish') is not None else None

        #logging.info(f"Extracted assignment: UID {uid}, TaskUID {task_uid}, ResourceUID {resource_uid}")
        assignments.append((uid, task_uid, resource_uid, milestone, percent_work_complete, units, work, actual_work, remaining_work, start, finish))

    return assignments

def extract_calendars(root):
    calendars = []
    for calendar in root.findall('./Calendars/Calendar'):
        uid = calendar.find('UID').text if calendar.find('UID') is not None else None
        name = calendar.find('Name').text if calendar.find('Name') is not None else None
        is_base_calendar = calendar.find('IsBaseCalendar').text if calendar.find('IsBaseCalendar') is not None else None
        base_calendar_uid = calendar.find('BaseCalendarUID').text if calendar.find('BaseCalendarUID') is not None else None

        #logging.info(f"Extracted calendar: {name}, UID: {uid}")
        calendars.append((uid, name, is_base_calendar, base_calendar_uid))

    return calendars

def extract_calendar_weekdays(root):
    calendar_weekdays = []
    for calendar in root.findall('./Calendars/Calendar'):
        calendar_uid = calendar.find('UID').text if calendar.find('UID') is not None else None
        for weekday in calendar.findall('./WeekDays/WeekDay'):
            day_type = weekday.find('DayType').text if weekday.find('DayType') is not None else None
            day_working = weekday.find('DayWorking').text if weekday.find('DayWorking') is not None else None

            for working_time in weekday.findall('./WorkingTimes/WorkingTime'):
                from_time = working_time.find('FromTime').text if working_time.find('FromTime') is not None else None
                to_time = working_time.find('ToTime').text if working_time.find('ToTime') is not None else None

                #logging.info(f"Extracted calendar weekday: {calendar_uid}, day type: {day_type}, day working: {day_working}, from time: {from_time}, to time: {to_time}")
                calendar_weekdays.append((calendar_uid, day_type, day_working, from_time, to_time))

    return calendar_weekdays

def extract_calendar_exceptions(root):
    calendar_exceptions = []
    for calendar in root.findall('./Calendars/Calendar'):
        calendar_uid = calendar.find('UID').text if calendar.find('UID') is not None else None
        for exception in calendar.findall('./Exceptions/Exception'):
            exception_uid = exception.find('UID').text if exception.find('UID') is not None else None
            name = exception.find('Name').text if exception.find('Name') is not None else None
            from_date = exception.find('FromDate').text if exception.find('FromDate') is not None else None
            to_date = exception.find('ToDate').text if exception.find('ToDate') is not None else None

            #logging.info(f"Extracted calendar exception: {calendar_uid}, exception UID: {exception_uid}")
            calendar_exceptions.append((calendar_uid, exception_uid, name, from_date, to_date))

    return calendar_exceptions

def insert_tasks_into_db(tasks, db_name):
    with sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS tasks')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                UID INTEGER PRIMARY KEY,
                ID INTEGER,
                Name TEXT,
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
                OutlineLevel INTEGER
            )
        ''')
        cursor.executemany('''
            INSERT INTO tasks (
                UID, ID, Name, Type, Priority, Start, Finish, Duration, Work, ActualWork, RemainingWork, Summary, Milestone, Notes, OutlineLevel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

# Example usage: Process and insert data from the XML file
if __name__ == "__main__":
    logging.info("Starting XML processing")
    process_xml('Skatteetaten - Modernisert Utvikleropplevelse - Nedstrippet for Analyse og plattform.xml', 'omniplan.db')
    logging.info("Finished XML processing")
