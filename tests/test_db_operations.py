import unittest
import sqlite3
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_operations import create_connection, insert_tasks_into_db

class TestDBOperations(unittest.TestCase):
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

    def test_insert_tasks_into_db(self):
        tasks = [
            (1, 1, 'Task 1', 1, 0, 500, '2023-01-01T00:00:00', '2023-01-02T00:00:00', '1d', '8h', '8h', '0h', 0, 0, 'Notes', None)
        ]
        insert_tasks_into_db(self.conn, tasks)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM omniplan_tasks')
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], 'Task 1')

if __name__ == '__main__':
    unittest.main()
