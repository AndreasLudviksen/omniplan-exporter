import unittest
import xml.etree.ElementTree as ET
import sqlite3
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xml_parse_operations import extract_tasks

class TestXMLParseOperations(unittest.TestCase):
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

    def test_extract_tasks(self):
        xml_string = '''
        <Project>
            <Tasks>
                <Task>
                    <UID>1</UID>
                    <ID>1</ID>
                    <Name>Task 1</Name>
                    <OutlineLevel>1</OutlineLevel>
                    <Type>0</Type>
                    <Priority>500</Priority>
                    <Start>2023-01-01T00:00:00</Start>
                    <Finish>2023-01-02T00:00:00</Finish>
                    <Duration>1d</Duration>
                    <Work>8h</Work>
                    <ActualWork>8h</ActualWork>
                    <RemainingWork>0h</RemainingWork>
                    <Summary>0</Summary>
                    <Milestone>0</Milestone>
                    <Notes>Notes</Notes>
                </Task>
            </Tasks>
        </Project>
        '''
        root = ET.fromstring(xml_string)
        tasks = extract_tasks(root)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][2], 'Task 1')

if __name__ == '__main__':
    unittest.main()
