# OmniPlan Exporter

This project processes an XML file and extracts various elements to insert into a SQLite database. It includes functionality to handle tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions. Additionally, it synchronizes tasks with Jira and generates various reports.

## Project Structure

- `omniplan_exporter/`: Main package containing the core functionality.
  - `db/`: Database-related functionality.
    - `operations.py`: Functions for database operations (e.g., create tables, insert data, read data).
  - `jira/`: Jira-related functionality.
    - `integration.py`: Functions for interacting with the Jira API.
  - `utils/`: Utility functions.
    - `validation.py`: Validation helpers (e.g., date, duration).
    - `conversions.py`: Conversion utilities (e.g., ISO 8601 to Jira format).
  - `sync.py`: Synchronization logic for syncing OmniPlan tasks with Jira.
  - `config.py`: Configuration constants (e.g., Jira API URLs, custom fields).
- `reports/`: Directory containing scripts for generating reports from the database.
  - `report_jira_task_description.py`: Generates a detailed report for a task including nested sub-tasks.
  - `report_milestones_top_level.py`: Generates a report listing top-level milestones.
  - `report_task_assignments_and_status.py`: Generates a report summarizing task assignments and their statuses.
- `tests/`: Directory containing unit tests for the project.
  - `test_db_operations.py`: Tests for database operations.
  - `test_validation.py`: Tests for validation utilities.
  - `test_sync.py`: Tests for synchronization logic.
  - `test_integration.py`: Tests for Jira integration.
- `requirements.txt`: Lists the dependencies required for the project.
- `setup.py`: Installation script for the project.

## How It Works

1. **XML Parsing**: The XML file is parsed using the `xml.etree.ElementTree` module.
2. **Data Extraction**: Various elements such as tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions are extracted from the XML.
3. **Database Insertion**: The extracted data is inserted into a SQLite database.
4. **Jira Synchronization**: Tasks are synchronized with Jira using the Jira API.
5. **Report Generation**: Report scripts in the `reports/` directory can be executed to generate various reports from the database.

## How to Run

1. **Install Dependencies**: Ensure you have Python installed. Install the required dependencies using:
   ```sh
   pip install -r requirements.txt
   ```
2. **Run the Main Script**: Execute the `main.py` script to process the XML file and insert data into the database.
   ```sh
   python main.py
   ```
3. **Synchronize with Jira**: Use the `sync.py` script to synchronize tasks with Jira.
   ```sh
   python -m omniplan_exporter.sync --db-path resources/omniplan.db --bearer-token YOUR_JIRA_TOKEN
   ```
4. **Run Report Scripts**: Execute the desired report script from the root of the project to generate a report.
   ```sh
   python reports/report_milestones_top_level.py
   ```

## Using `setup.py`

You can install the project as a package using the `setup.py` file. This allows you to use the project as a command-line tool or import its modules in other Python scripts.

1. **Install the Package**:
   ```sh
   python setup.py install
   ```

2. **Use the Command-Line Tool**:
   After installation, you can run the synchronization script directly:
   ```sh
   omniplan-sync --db-path resources/omniplan.db --bearer-token YOUR_JIRA_TOKEN
   ```

3. **Uninstall the Package**:
   If needed, you can uninstall the package using `pip`:
   ```sh
   pip uninstall omniplan-exporter
   ```

## Running Tests

To run the tests, you can use `pytest` or `ptw` (pytest-watch) for continuous testing.

1. **Run Tests with pytest**:
   ```sh
   pytest
   ```

2. **Run Tests with unittest**:
   ```sh
   ptw
   ```

## Example Usage

The `main.py` script processes the provided XML file and inserts the data into a SQLite database named `resources/omniplan.db`. The script logs the progress and any errors encountered during the process.

```python
if __name__ == "__main__":
    logging.info("Starting XML processing")
    process_xml('omniplan.xml', 'resources/omniplan.db')
    logging.info("Finished XML processing")
```

## License

This project is licensed under the MIT License.