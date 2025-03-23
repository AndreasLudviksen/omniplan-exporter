import sys
import os
import sqlite3
import logging
from datetime import datetime

from omniplan_exporter.db import operations

logger = logging.getLogger(__name__)


def generate_milestones_top_level_report(db_path, output_dir="resources/reports"):
    conn = sqlite3.connect(db_path)
    try:
        milestones = operations.get_tasks_by_outline(conn, outline_level=1, milestone=1)
        milestones = sorted(
            milestones,
            key=lambda x: datetime.fromisoformat(x[2]).date() if x[2] else datetime.max,
        )

        operations.create_report_directory()
        report_filename = os.path.join(output_dir, "milestones-top-level.md")
        with open(report_filename, "w") as report_file:
            report_file.write("# Milepæler Modernisert Utvikleropplevelse\n\n")
            report_file.write("| Milepæl | Dato | Forutsetter | Muliggjør |\n")
            report_file.write("|-----------|------|-------------|-----------|\n")
            for milestone in milestones:
                uid, name, finish, _, _, _ = milestone
                finish_date = datetime.fromisoformat(finish).date() if finish else "N/A"

                dependencies = operations.get_task_dependencies(
                    conn, milestone_id=uid, dependency_type="predecessor"
                )
                dependents = operations.get_task_dependencies(
                    conn, milestone_id=uid, dependency_type="successor"
                )

                dependencies_names = "<br>".join(
                    [f"- {dep['Name']}" for dep in dependencies]
                )
                dependents_names = "<br>".join(
                    [f"- {dep['Name']}" for dep in dependents]
                )

                report_file.write(
                    (
                        f"| {name} | {finish_date} | {dependencies_names} | "
                        f"{dependents_names} |\n"
                    )
                )

            report_file.write(f"\nDenne rapporten ble generert {datetime.now().date()}")

        logger.info(f"Report generated: {report_filename}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    db_path = os.path.join(os.path.dirname(__file__), "../resources/omniplan.db")
    output_dir = "resources/reports"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    generate_milestones_top_level_report(db_path, output_dir)
