import sys
import os
import sqlite3
from datetime import datetime

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_read_operations import create_report_directory, get_tasks_by_outline, get_task_dependencies

def generate_milestones_top_level_report(db_path, output_dir='resources/reports'):
    conn = sqlite3.connect(db_path)
    try:
        milestones = get_tasks_by_outline(conn, outline_level=1, milestone=1)
        milestones = sorted(milestones, key=lambda x: datetime.fromisoformat(x[2]).date() if x[2] else datetime.max)

        create_report_directory()
        report_filename = os.path.join(output_dir, "milestones-top-level.md")
        with open(report_filename, 'w') as report_file:
            report_file.write("# Milepæler Modernisert Utvikleropplevelse\n\n")
            report_file.write("| Milepæl | Dato | Forutsetter | Muliggjør |\n")
            report_file.write("|-----------|------|-------------|-----------|\n")
            for milestone in milestones:
                uid, name, finish = milestone
                finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"
                
                dependencies = get_task_dependencies(conn, milestone_id=uid, dependency_type='predecessor')
                dependents = get_task_dependencies(conn, milestone_id=uid, dependency_type='successor')
                
                dependencies_names = "<br>".join([f"- {dep['Name']}" for dep in dependencies])
                dependents_names = "<br>".join([f"- {dep['Name']}" for dep in dependents])
                
                report_file.write(f"| {name} | {finish_date} | {dependencies_names} | {dependents_names} |\n")
            
            report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}")

        print(f"Report generated: {report_filename}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), '../resources/omniplan.db')
    output_dir = 'resources/reports'
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    generate_milestones_top_level_report(db_path, output_dir)