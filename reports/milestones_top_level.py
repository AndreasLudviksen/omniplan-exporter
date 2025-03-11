import sys
import os
import sqlite3
from datetime import datetime
from report_utils import create_report_directory, get_tasks_by_outline

def generate_milestones_top_level_report(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        milestones = get_tasks_by_outline(db_path, outline_level=1, milestone=1)
        # Sort milestones by finish date
        milestones = sorted(milestones, key=lambda x: datetime.fromisoformat(x[1]).date() if x[1] else datetime.max)

        create_report_directory()
        report_filename = os.path.join('resources/reports', "Milestones_top_level.md")
        with open(report_filename, 'w') as report_file:
            report_file.write("# Milepæler Modernisert Utvikleropplevelse\n\n")
            report_file.write("| Milepæl | Dato |\n")
            report_file.write("|-----------|------|\n")
            for name, finish in milestones:
                finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"
                report_file.write(f"| {name} | {finish_date} |\n")
            
            # Add the generation date at the end of the report
            report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}")

        print(f"Report generated: {report_filename}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), '../resources/omniplan.db')  # Update the path to the database
    generate_milestones_top_level_report(db_path)
