import xml.etree.ElementTree as ET
import logging
import os
from db_operations import (
    create_connection, insert_tasks_into_db, insert_resources_into_db, insert_assignments_into_db,
    insert_calendars_into_db, insert_calendar_weekdays_into_db, insert_calendar_exceptions_into_db,
    insert_extended_attributes_into_db, insert_predecessor_links_into_db
)
from xml_parse_operations import (
    extract_tasks, extract_resources, extract_assignments,
    extract_calendars, extract_calendar_weekdays, extract_calendar_exceptions,
    extract_extended_attributes, extract_predecessor_links
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def strip_namespace(xml_string):
    return xml_string.replace(' xmlns="http://schemas.microsoft.com/project"', '')

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
        # Ensure the resources directory exists
        os.makedirs(os.path.dirname(db_name), exist_ok=True)

        # Read and strip the namespace from the XML file
        with open(file_path, 'r') as file:
            xml_string = file.read()
        xml_string = strip_namespace(xml_string)

        # Parse the XML file
        root = ET.fromstring(xml_string)

        # Create a database connection
        conn = create_connection(db_name)

        # Extract and insert tasks
        tasks = extract_tasks(root)
        insert_tasks_into_db(conn, tasks)

        # Extract and insert resources
        resources = extract_resources(root)
        insert_resources_into_db(conn, resources)

        # Extract and insert assignments
        assignments = extract_assignments(root)
        insert_assignments_into_db(conn, assignments)

        # Extract and insert calendars
        calendars = extract_calendars(root)
        insert_calendars_into_db(conn, calendars)

        # Extract and insert calendar weekdays
        calendar_weekdays = extract_calendar_weekdays(root)
        insert_calendar_weekdays_into_db(conn, calendar_weekdays)

        # Extract and insert calendar exceptions
        calendar_exceptions = extract_calendar_exceptions(root)
        insert_calendar_exceptions_into_db(conn, calendar_exceptions)

        # Extract and insert extended attributes
        extended_attributes = extract_extended_attributes(root)
        insert_extended_attributes_into_db(conn, extended_attributes)

        # Extract and insert predecessor links
        predecessor_links = extract_predecessor_links(root)
        insert_predecessor_links_into_db(conn, predecessor_links)

    except ET.ParseError as e:
        logging.error(f"Error parsing XML: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Example usage: Process and insert data from the XML file
if __name__ == "__main__":
    logging.info("Starting XML processing")
    process_xml('<XML Input>', 'resources/omniplan.db')
    logging.info("Finished XML processing")
