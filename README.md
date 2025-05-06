# OmniPlan Exporter

This project processes an export from Omniplan (as an XML file) and migrates the data to a SQLite database. 
The project offers synchronization of Jira tasks, and producese reports from the data in the database.

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
- `reports/`: Directory containing scripts for generating reports from the database.
  - `report_jira_task_description.py`: Generates a detailed report for a task including nested sub-tasks.
  - `report_milestones_top_level.py`: Generates a report listing top-level milestones.
  - `report_task_assignments_and_status.py`: Generates a report summarizing task assignments and their statuses.
  - `report_stakeholders_from_jira.py`: Generates a pivot table of stakeholders for tasks with outline level 2, filtered by specific parent UIDs. The report includes task names, stakeholder names, and roles.
  - `report_diff_jira_omniplan.py`: Generates a comparison report between tasks in Jira and OmniPlan, highlighting mismatches and tasks exclusive to one system.
- `tests/`: Directory containing unit tests for the project.
  - `test_db_operations.py`: Tests for database operations.
  - `test_validation.py`: Tests for validation utilities.
  - `test_sync.py`: Tests for synchronization logic.
  - `test_integration.py`: Tests for Jira integration.
- `requirements.txt`: Lists the dependencies required for the project.
- `.env`: Environment variables file for configuration.

## How It Works

1. **XML Parsing**: The XML file is parsed using the `xml.etree.ElementTree` module.
2. **Data Extraction**: Various elements such as tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions are extracted from the XML.
3. **Database Insertion**: The extracted data is inserted into a SQLite database.
4. **Jira Synchronization**: Tasks are synchronized with Jira using the Jira API.
5. **Report Generation**: Report scripts in the `reports/` directory can be executed to generate various reports from the database, including task descriptions, milestones, assignments, stakeholders, and differences between Jira and OmniPlan.

## Configuration with `.env`

The project uses a `.env` file to manage configuration variables. Create a `.env` file in the root of the project with the following content:

```properties
JIRA_BASE_URL=<jira base url>
XML_FILE_PATH=<relative path to the xml file exported from OmniPlan>
DB_FILE_PATH=<location to store the sqlite db file>
```

- `JIRA_BASE_URL`: The base URL of your Jira instance.
- `XML_FILE_PATH`: The path to the XML file to be processed.
- `DB_FILE_PATH`: The path to the SQLite database file.

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
4. **Create Jira Epic and Subtasks**: Creates a Jira epic and its subtasks for a given OmniPlan task UID.
   ```sh
   python -m omniplan_exporter.create_jira_epic --db-path <db_path> --omniplan-uid <task_uid> --bearer-token <jira_token> [--dry-run]
   ```
5. **Run Milestones Report**: Execute the desired report script from the root of the project to generate a report.
   ```sh
   python reports/report_milestones_top_level.py
   ```
6. **Stakeholders Report**: Generates a pivot table of stakeholders for tasks with outline level 2, filtered by specific parent UIDs. The report includes task names, stakeholder names, and roles.
   ```sh
   python reports/report_stakeholders_from_jira.py <bearer_token>
   ```

7. **Diff Report**: Generates a comparison report between tasks in Jira and OmniPlan, highlighting mismatches and tasks exclusive to one system.
   ```sh
   python reports/report_diff_jira_omniplan.py <jira_task> <bearer_token>
   ```

8. **Task Assignments and Status Report**: Generates a report summarizing task assignments and their statuses.
   ```sh
   python reports/report_task_assignments_and_status.py <jira_task>
   ```

9. **Jira Task Description Report**: Generates a detailed report for a task, including nested sub-tasks.
   ```sh
   python reports/report_jira_task_description.py <jira_task> [output_dir]
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

## Code Formatting and Linting

This project uses `black` for code formatting and `flake8` for linting to ensure code quality and consistency.

### Pre-commit Hook
To ensure code is formatted and linted before committing, you can set up a pre-commit hook using the `.pre-commit-config.yaml` file. Install `pre-commit` and set up the hooks with the following commands:
```bash
pip install pre-commit
pre-commit install
```
This will automatically run `black` and `flake8` on staged files before each commit.

### Formatting with Black
To format the codebase using `black`, you can run the following command:
```bash
make format
```
This command is defined in the `Makefile` and will apply `black` formatting to all files in the project.

### Linting with Flake8
To lint the codebase using `flake8`, you can run:
```bash
make lint
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