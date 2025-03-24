import unittest
import sqlite3
from dotenv import load_dotenv
from omniplan_exporter.db import operations

# Load environment variables
load_dotenv()


class TestDBOperations(unittest.TestCase):
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

    def test_insert_tasks_into_db(self):
        tasks = [
            (
                1,
                1,
                "Task 1",
                1,
                0,
                500,
                "2023-01-01T00:00:00",
                "2023-01-02T00:00:00",
                "1d",
                "8h",
                "8h",
                "0h",
                0,
                0,
                "Notes",
                None,
                50,
            )
        ]
        operations.insert_tasks_into_db(self.conn, tasks)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM omniplan_tasks")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "Task 1")

    def test_insert_assignments_into_db(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name) VALUES (1, "Task 1")')
        self.conn.execute(
            'INSERT INTO omniplan_resources (UID, Name) VALUES (1, "Resource 1")'
        )
        assignments = [
            (
                1,
                1,
                1,
                0,
                100,
                1.0,
                "8h",
                "8h",
                "0h",
                "2023-01-01T00:00:00",
                "2023-01-02T00:00:00",
            )
        ]
        operations.insert_assignments_into_db(self.conn, assignments)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM omniplan_assignments")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 1)

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

    def test_create_tasks_table(self):
        cursor = self.conn.cursor()
        operations.create_tasks_table(cursor)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='omniplan_tasks'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_create_extended_attributes_table(self):
        cursor = self.conn.cursor()
        operations.create_extended_attributes_table(cursor)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='omniplan_task_extended_attributes'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_create_predecessor_links_table(self):
        cursor = self.conn.cursor()
        operations.create_predecessor_links_table(cursor)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='omniplan_predecessor_links'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_create_resources_table(self):
        cursor = self.conn.cursor()
        operations.create_resources_table(cursor)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='omniplan_resources'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_create_assignments_table(self):
        cursor = self.conn.cursor()
        operations.create_assignments_table(cursor)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='omniplan_assignments'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_insert_extended_attributes_into_db(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name) VALUES (1, "Task 1")')
        attributes = [
            (1, 188743731, "epos"),
        ]
        operations.insert_extended_attributes_into_db(self.conn, attributes)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM omniplan_task_extended_attributes")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "epos")

    def test_insert_predecessor_links_into_db(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name) VALUES (1, "Task 1")')
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name) VALUES (2, "Task 2")')
        links = [
            (1, 2, "1d"),
        ]
        operations.insert_predecessor_links_into_db(self.conn, links)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM omniplan_predecessor_links")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 2)

    def test_insert_resources_into_db(self):
        resources = [
            (1, "Resource 1", "Notes", 100, 0, 0, 0),
        ]
        operations.insert_resources_into_db(self.conn, resources)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM omniplan_resources")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Resource 1")

    def test_get_assignments_by_uid(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name) VALUES (1, "Task 1")')
        self.conn.execute(
            'INSERT INTO omniplan_resources (UID, Name) VALUES (1, "Resource 1")'
        )
        self.conn.execute(
            "INSERT INTO omniplan_assignments (UID, TaskUID, ResourceUID, Units) VALUES (1, 1, 1, 1.0)"
        )
        result = operations.get_assignments_by_uid(self.conn, 1)
        self.assertIsNotNone(result)
        for resource_name, units in result:
            self.assertEqual(resource_name, "Resource 1")
            self.assertEqual(units, 1.0)


if __name__ == "__main__":
    unittest.main()
