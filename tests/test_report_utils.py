import unittest
import sqlite3
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reports.report_utils import get_parent_task, get_sub_tasks, get_assignments_for_task_and_subtasks
from db_operations import (
    create_tasks_table, create_extended_attributes_table, create_predecessor_links_table,
    create_resources_table, create_assignments_table
)

class TestReportUtils(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('PRAGMA foreign_keys = ON')
        cursor = self.conn.cursor()
        create_tasks_table(cursor)
        create_extended_attributes_table(cursor)
        create_predecessor_links_table(cursor)
        create_resources_table(cursor)
        create_assignments_table(cursor)

    def tearDown(self):
        self.conn.close()

    def test_get_parent_task(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish) VALUES (1, "Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00")')
        self.conn.execute('INSERT INTO omniplan_task_extended_attributes (TaskUID, FieldID, Value) VALUES (1, 188743731, "epos")')
        result = get_parent_task(self.conn, "epos")
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Task 1")

    def test_get_sub_tasks(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish) VALUES (1, "Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00")')
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish, ParentUID, Milestone) VALUES (2, "Sub Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00", 1, 0)')
        sub_tasks, _ = get_sub_tasks(self.conn, 1)
        self.assertEqual(len(sub_tasks), 1)
        self.assertEqual(sub_tasks[0][1], "Sub Task 1")

    def test_get_assignments_for_task_and_subtasks(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish) VALUES (1, "Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00")')
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name, Notes, Start, Finish, ParentUID) VALUES (2, "Sub Task 1", "Notes", "2023-01-01T00:00:00", "2023-01-02T00:00:00", 1)')
        self.conn.execute('INSERT INTO omniplan_resources (UID, Name) VALUES (1, "Resource 1")')
        self.conn.execute('INSERT INTO omniplan_assignments (UID, TaskUID, ResourceUID, Milestone, PercentWorkComplete, Units, Work, ActualWork, RemainingWork, Start, Finish) VALUES (1, 1, 1, 0, 100, 1.0, "8h", "8h", "0h", "2023-01-01T00:00:00", "2023-01-02T00:00:00")')
        self.conn.execute('INSERT INTO omniplan_assignments (UID, TaskUID, ResourceUID, Milestone, PercentWorkComplete, Units, Work, ActualWork, RemainingWork, Start, Finish) VALUES (2, 2, 1, 0, 100, 1.0, "8h", "8h", "0h", "2023-01-01T00:00:00", "2023-01-02T00:00:00")')
        self.conn.execute('INSERT INTO omniplan_task_extended_attributes (TaskUID, FieldID, Value) VALUES (1, 188743731, "epos")')
        
        assignments = get_assignments_for_task_and_subtasks(self.conn, 1)
        self.assertEqual(len(assignments), 2)
        self.assertEqual(assignments[0][1], "Task 1")
        self.assertEqual(assignments[0][2], "Resource 1")
        self.assertEqual(assignments[0][7], "epos")
        self.assertEqual(assignments[1][1], "Sub Task 1")

if __name__ == '__main__':
    unittest.main()
