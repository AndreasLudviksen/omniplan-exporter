import unittest
import sqlite3
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reports.report_utils import get_parent_task, get_sub_tasks

class TestReportUtils(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS omniplan_tasks (
                UID INTEGER PRIMARY KEY,
                ID INTEGER,
                Name TEXT,
                OutlineLevel INTEGER,
                Type INTEGER,
                Priority INTEGER,
                Start DATETIME,
                Finish DATETIME,
                Duration TEXT,
                Work TEXT,
                ActualWork TEXT,
                RemainingWork TEXT,
                Summary INTEGER,
                Milestone INTEGER,
                Notes TEXT,
                ParentUID INTEGER,
                FOREIGN KEY (ParentUID) REFERENCES omniplan_tasks(UID)
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS omniplan_task_extended_attributes (
                TaskUID INTEGER,
                FieldID INTEGER,
                Value TEXT,
                FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID)
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS omniplan_predecessor_links (
                TaskUID INTEGER,
                PredecessorUID INTEGER,
                Type INTEGER,
                FOREIGN KEY (TaskUID) REFERENCES omniplan_tasks(UID),
                FOREIGN KEY (PredecessorUID) REFERENCES omniplan_tasks(UID)
            )
        ''')

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

if __name__ == '__main__':
    unittest.main()
