import unittest
import sqlite3
import os
from dotenv import load_dotenv
from omniplan_exporter.db import operations

# Load environment variables
load_dotenv()


class TestDBReadOperations(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        cursor = self.conn.cursor()
        operations.create_tasks_table(cursor)
        operations.create_extended_attributes_table(cursor)
        operations.create_predecessor_links_table(cursor)
        operations.create_resources_table(cursor)
        operations.create_assignments_table(cursor)

    def tearDown(self):
        self.conn.close()

    def test_get_parent_task(self):
        self.conn.execute(
            'INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish) VALUES (1, "Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00")'
        )
        self.conn.execute(
            'INSERT INTO omniplan_task_extended_attributes (TaskUID, FieldID, Value) VALUES (1, 188743731, "epos")'
        )
        result = operations.get_parent_task(self.conn, "epos")
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Task 1")

    def test_get_sub_tasks(self):
        self.conn.execute(
            'INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish) VALUES (1, "Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00")'
        )
        self.conn.execute(
            'INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish, ParentUID, Milestone) VALUES (2, "Sub Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00", 1, 0)'
        )
        sub_tasks, _ = operations.get_sub_tasks(self.conn, 1)
        self.assertEqual(len(sub_tasks), 1)
        self.assertEqual(sub_tasks[0][1], "Sub Task 1")


if __name__ == "__main__":
    unittest.main()
