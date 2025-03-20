import unittest
import sqlite3
from dotenv import load_dotenv
from omniplan_exporter.db import operations

# Load environment variables
load_dotenv()

class TestDBWriteOperations(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('PRAGMA foreign_keys = ON')
        cursor = self.conn.cursor()
        operations.create_tasks_table(cursor)
        operations.create_resources_table(cursor)
        operations.create_assignments_table(cursor)
        operations.create_predecessor_links_table(cursor)

    def tearDown(self):
        self.conn.close()

    def test_insert_tasks_into_db(self):
        tasks = [
            (1, 1, 'Task 1', 1, 0, 500, '2023-01-01T00:00:00', '2023-01-02T00:00:00', '1d', '8h', '8h', '0h', 0, 0, 'Notes', None, 50)
        ]
        operations.insert_tasks_into_db(self.conn, tasks)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM omniplan_tasks')
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], 'Task 1')

    def test_insert_assignments_into_db(self):
        self.conn.execute('INSERT INTO omniplan_tasks (UID, Name) VALUES (1, "Task 1")')
        self.conn.execute('INSERT INTO omniplan_resources (UID, Name) VALUES (1, "Resource 1")')
        assignments = [
            (1, 1, 1, 0, 100, 1.0, '8h', '8h', '0h', '2023-01-01T00:00:00', '2023-01-02T00:00:00')
        ]
        operations.insert_assignments_into_db(self.conn, assignments)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM omniplan_assignments')
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 1)

if __name__ == '__main__':
    unittest.main()
