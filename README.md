# XML to SQLite Processor

This project processes an XML file and extracts various elements to insert into a SQLite database. It includes functionality to handle tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions.

## Project Structure

- `main.py`: The main module that processes the XML file and inserts data into the SQLite database.
- `db_operations.py`: Module containing functions for database operations.
- `reports/`: Directory containing scripts for generating reports from the database.
  - `jira_task_description.py`: Generates a detailed report for a task including nested sub-tasks.
  - `milestones_top_level.py`: Generates a report listing top-level milestones.

## How It Works

1. **XML Parsing**: The XML file is parsed using the `xml.etree.ElementTree` module.
2. **Data Extraction**: Various elements such as tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions are extracted from the XML.
3. **Database Insertion**: The extracted data is inserted into a SQLite database.
4. **Report Generation**: Report scripts in the `reports/` directory can be executed to generate various reports from the database.

## How to Run

1. **Install Dependencies**: Ensure you have Python installed. No additional dependencies are required as the project uses standard libraries.
2. **Run the Main Script**: Execute the `main.py` script to process the XML file and insert data into the database.
   ```sh
   python main.py
   ```
3. **Run Report Scripts**: Execute the desired report script from the `reports/` directory to generate a report.
   ```sh
   python milestones_top_level.py
   ```

## Example Usage

The `main.py` script processes the provided XML file and inserts the data into a SQLite database named `omniplan.db`. The script logs the progress and any errors encountered during the process.

```python
if __name__ == "__main__":
    logging.info("Starting XML processing")
    process_xml('omniplan.xml')
    logging.info("Finished XML processing")
```

## License

This project is licensed under the MIT License.