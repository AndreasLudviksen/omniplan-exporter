import unittest
import xml.etree.ElementTree as ET
import sqlite3
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xml_parse_operations import extract_tasks
from db_operations import create_tasks_table, create_predecessor_links_table

class TestXMLParseOperations(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('PRAGMA foreign_keys = ON')
        cursor = self.conn.cursor()
        create_tasks_table(cursor)
        create_predecessor_links_table(cursor)

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
