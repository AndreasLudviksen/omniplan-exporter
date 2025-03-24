import os
import subprocess
import unittest


class TestReportGeneration(unittest.TestCase):
    def setUp(self):
        # Ensure the test resources directory exists
        self.output_dir = "tests/resources/reports"
        os.makedirs(self.output_dir, exist_ok=True)

        # Clean up any existing report files
        self.files_to_check = [
            os.path.join(self.output_dir, "jira-task-description-MUP-1.txt"),
            os.path.join(self.output_dir, "task-assignments-and-status-MUP-24.md"),
            os.path.join(self.output_dir, "milestones-top-level.md"),
        ]
        for file in self.files_to_check:
            if os.path.exists(file):
                os.remove(file)

    def test_report_generation(self):
        # Run the commands to generate the reports
        subprocess.run(
            [
                "python",
                "reports/report_jira_task_description.py",
                "mup-1",
                self.output_dir,
            ],
            check=True,
        )
        subprocess.run(
            [
                "python",
                "reports/report_task_assignments_and_status.py",
                "mup-24",
                self.output_dir,
            ],
            check=True,
        )
        subprocess.run(
            ["python", "reports/report_milestones_top_level.py", self.output_dir],
            check=True,
        )

        # Verify that the files are created
        for file in self.files_to_check:
            self.assertTrue(
                os.path.exists(file), f"Expected file {file} was not created."
            )

    def tearDown(self):
        # Clean up generated files after the test
        for file in self.files_to_check:
            if os.path.exists(file):
                os.remove(file)


if __name__ == "__main__":
    unittest.main()
