# XML to SQLite Processor

This project processes an XML file and extracts various elements to insert into a SQLite database. It includes functionality to handle tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions.

## Project Structure

- `main.py`: The main module that processes the XML file and inserts data into the SQLite database.
- `test_main.py`: Unit tests for the main module.
- `Skatteetaten - Modernisert Utvikleropplevelse - Nedstrippet for Analyse og plattform.xml`: Sample XML file used for processing.

## How It Works

1. **XML Parsing**: The XML file is parsed using the `xml.etree.ElementTree` module.
2. **Data Extraction**: Various elements such as tasks, resources, assignments, calendars, calendar weekdays, and calendar exceptions are extracted from the XML.
3. **Database Insertion**: The extracted data is inserted into a SQLite database.

## How to Run

1. **Install Dependencies**: Ensure you have Python installed. No additional dependencies are required as the project uses standard libraries.
2. **Run the Main Script**: Execute the `main.py` script to process the XML file and insert data into the database.
   ```sh
   python main.py
   ```

## Running Unit Tests

Unit tests are provided to ensure the correctness of the XML processing and database insertion functions. To run the tests, use the following command:

```sh
python -m unittest test_main.py
```

## Example Usage

The `main.py` script processes the provided XML file and inserts the data into a SQLite database named `omniplan.db`. The script logs the progress and any errors encountered during the process.

```python
if __name__ == "__main__":
    logging.info("Starting XML processing")
    process_xml('Skatteetaten - Modernisert Utvikleropplevelse - Nedstrippet for Analyse og plattform.xml')
    logging.info("Finished XML processing")
```

## License

This project is licensed under the MIT License.
````