import xml.etree.ElementTree as ET
from datetime import datetime
import logging

def extract_tasks(root):
    tasks = []
    seen_uids = set()
    parent_stack = []

    for task in root.findall('./Tasks/Task'):
        uid = task.find('UID').text if task.find('UID') is not None else None
        if uid in seen_uids:
            logging.error(f"Detected duplicate task uid: {uid}")
            continue
        seen_uids.add(uid)

        task_id = task.find('ID').text if task.find('ID') is not None else None
        name = task.find('Name').text if task.find('Name') is not None else None
        task_type = task.find('Type').text if task.find('Type') is not None else None
        priority = task.find('Priority').text if task.find('Priority') is not None else None

        start_str = task.find('Start').text if task.find('Start') is not None else None
        finish_str = task.find('Finish').text if task.find('Finish') is not None else None
        start = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S") if start_str else None
        finish = datetime.strptime(finish_str, "%Y-%m-%dT%H:%M:%S") if finish_str else None

        duration = task.find('Duration').text if task.find('Duration') is not None else None
        work = task.find('Work').text if task.find('Work') is not None else None
        actual_work = task.find('ActualWork').text if task.find('ActualWork') is not None else None
        remaining_work = task.find('RemainingWork').text if task.find('RemainingWork') is not None else None
        summary = int(task.find('Summary').text) if task.find('Summary') is not None else None
        milestone = int(task.find('Milestone').text) if task.find('Milestone') is not None else None
        notes = task.find('Notes').text if task.find('Notes') is not None else None
        outline_level = int(task.find('OutlineLevel').text) if task.find('OutlineLevel') is not None else None
        percent_complete = float(task.find('PercentComplete').text) if task.find('PercentComplete') is not None else None

        # Determine the parent UID based on the outline level
        while parent_stack and parent_stack[-1][1] >= outline_level:
            parent_stack.pop()
        parent_uid = parent_stack[-1][0] if parent_stack else None
        parent_stack.append((uid, outline_level))

        #logging.info(f"Extracted task: {name}, start: {start}")
        tasks.append((uid, task_id, name, outline_level, task_type, priority, start, finish, duration, work, actual_work, remaining_work, summary, milestone, notes, parent_uid, percent_complete))

    return tasks

def extract_resources(root):
    resources = []
    for resource in root.findall('./Resources/Resource'):
        uid = resource.find('UID').text if resource.find('UID') is not None else None
        resource_id = resource.find('ID').text if resource.find('ID') is not None else None
        name = resource.find('Name').text if resource.find('Name') is not None else None
        resource_type = resource.find('Type').text if resource.find('Type') is not None else None
        max_units = resource.find('MaxUnits').text if resource.find('MaxUnits') is not None else None
        calendar_uid = resource.find('CalendarUID').text if resource.find('CalendarUID') is not None else None
        group = resource.find('Group').text if resource.find('Group') is not None else None

        #logging.info(f"Extracted resource: {name}, group: {group}")
        resources.append((uid, resource_id, name, resource_type, max_units, calendar_uid, group))

    return resources

def extract_assignments(root):
    assignments = []
    for assignment in root.findall('./Assignments/Assignment'):
        uid = assignment.find('UID').text if assignment.find('UID') is not None else None
        task_uid = assignment.find('TaskUID').text if assignment.find('TaskUID') is not None else None
        resource_uid = assignment.find('ResourceUID').text if assignment.find('ResourceUID') is not None else None
        milestone = assignment.find('Milestone').text if assignment.find('Milestone') is not None else None
        percent_work_complete = assignment.find('PercentWorkComplete').text if assignment.find('PercentWorkComplete') is not None else None
        units = assignment.find('Units').text if assignment.find('Units') is not None else None
        work = assignment.find('Work').text if assignment.find('Work') is not None else None
        actual_work = assignment.find('ActualWork').text if assignment.find('ActualWork') is not None else None
        remaining_work = assignment.find('RemainingWork').text if assignment.find('RemainingWork') is not None else None
        start = assignment.find('Start').text if assignment.find('Start') is not None else None
        finish = assignment.find('Finish').text if assignment.find('Finish') is not None else None

        #logging.info(f"Extracted assignment: UID {uid}, TaskUID {task_uid}, ResourceUID {resource_uid}")
        assignments.append((uid, task_uid, resource_uid, milestone, percent_work_complete, units, work, actual_work, remaining_work, start, finish))

    return assignments

def extract_calendars(root):
    calendars = []
    for calendar in root.findall('./Calendars/Calendar'):
        uid = calendar.find('UID').text if calendar.find('UID') is not None else None
        name = calendar.find('Name').text if calendar.find('Name') is not None else None
        is_base_calendar = calendar.find('IsBaseCalendar').text if calendar.find('IsBaseCalendar') is not None else None
        base_calendar_uid = calendar.find('BaseCalendarUID').text if calendar.find('BaseCalendarUID') is not None else None

        #logging.info(f"Extracted calendar: {name}, UID: {uid}")
        calendars.append((uid, name, is_base_calendar, base_calendar_uid))

    return calendars

def extract_calendar_weekdays(root):
    calendar_weekdays = []
    for calendar in root.findall('./Calendars/Calendar'):
        calendar_uid = calendar.find('UID').text if calendar.find('UID') is not None else None
        for weekday in calendar.findall('./WeekDays/WeekDay'):
            day_type = weekday.find('DayType').text if weekday.find('DayType') is not None else None
            day_working = weekday.find('DayWorking').text if weekday.find('DayWorking') is not None else None

            for working_time in weekday.findall('./WorkingTimes/WorkingTime'):
                from_time = working_time.find('FromTime').text if working_time.find('FromTime') is not None else None
                to_time = working_time.find('ToTime').text if working_time.find('ToTime') is not None else None

                #logging.info(f"Extracted calendar weekday: {calendar_uid}, day type: {day_type}, day working: {day_working}, from time: {from_time}, to time: {to_time}")
                calendar_weekdays.append((calendar_uid, day_type, day_working, from_time, to_time))

    return calendar_weekdays

def extract_calendar_exceptions(root):
    calendar_exceptions = []
    for calendar in root.findall('./Calendars/Calendar'):
        calendar_uid = calendar.find('UID').text if calendar.find('UID') is not None else None
        for exception in calendar.findall('./Exceptions/Exception'):
            exception_uid = exception.find('UID').text if exception.find('UID') is not None else None
            name = exception.find('Name').text if exception.find('Name') is not None else None
            from_date = exception.find('FromDate').text if exception.find('FromDate') is not None else None
            to_date = exception.find('ToDate').text if exception.find('ToDate') is not None else None

            #logging.info(f"Extracted calendar exception: {calendar_uid}, exception UID: {exception_uid}")
            calendar_exceptions.append((calendar_uid, exception_uid, name, from_date, to_date))

    return calendar_exceptions

def extract_extended_attributes(root):
    """
    Extracts extended attributes from the XML root element.

    Args:
        root (Element): The root element of the XML tree.

    Returns:
        list: A list of tuples containing extended attribute data.
    """
    extended_attributes = []
    for task in root.findall('.//Task'):
        task_uid = task.find('UID').text if task.find('UID') is not None else None
        for ext_attr in task.findall('.//ExtendedAttribute'):
            field_id = ext_attr.find('FieldID').text if ext_attr.find('FieldID') is not None else None
            value = ext_attr.find('Value').text if ext_attr.find('Value') is not None else None
            extended_attributes.append((task_uid, field_id, value))
    return extended_attributes

def extract_predecessor_links(root):
    """
    Extracts predecessor links from the XML root element.

    Args:
        root (Element): The root element of the XML tree.

    Returns:
        list: A list of tuples containing predecessor link data.
    """
    predecessor_links = []
    for task in root.findall('.//Task'):
        task_uid = task.find('UID').text
        for link in task.findall('PredecessorLink'):
            predecessor_uid = link.find('PredecessorUID').text
            link_type = link.find('Type').text
            predecessor_links.append((task_uid, predecessor_uid, link_type))
    return predecessor_links