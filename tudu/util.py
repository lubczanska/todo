"""Utility functions used by other modules"""
import datetime
import os
import pwd

import tudu.exception as exception


def add_s(word: str, number: int):
    """ Add s to the end of a word if necessary """
    return word if number == 1 else word + 's'


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def task_info_str(task) -> tuple[str, str, tuple[str, bool], str, int]:
    """ Format task information for printing """
    done = '✓' if task.done else ' '
    deadline = date_pprinter(task.deadline) if task.deadline else ('', False)
    notes = task.notes if task.notes else ''
    return task.name, done, deadline, notes, task.priority


def calculate_notification(task) -> datetime:
    """ Calculate time of the next notification """
    if task.priority == 3:
        time = datetime.datetime.today() + datetime.timedelta(1)
    elif task.priority == 2:
        time = task.deadline - datetime.timedelta(7)
    elif task.priority == 1:
        time = task.deadline - datetime.timedelta(2)
    else:
        time = task.deadline + datetime.timedelta(1)
    return time


def date_add_days(delta: int, date: datetime = datetime.datetime.today()) -> datetime:
    return date + datetime.timedelta(days=delta)


def time_until_date(date: datetime) -> int:
    """ Returns days until date """
    if date is None:
        return 1000000000  # maybe not the smartest way to do it, but whatever
    today = datetime.datetime.today()
    delta = (date.date() - today.date()).days
    return delta


def time_to_notify(date: datetime) -> bool:
    """ Is it time to send a notification yet? """
    if not date:
        return False
    today = datetime.datetime.today()
    delta = (date - today).total_seconds()
    return delta < 0


def date_parser(date: str) -> datetime:
    """ Parse user input date to datetime format """
    today = datetime.datetime.today()
    if date == 'today':
        return today
    elif date == 'tomorrow':
        return today + datetime.timedelta(days=1)
    elif date == 'yesterday':
        return today + datetime.timedelta(days=-1)
    else:
        days = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
        if date[:3] in days.keys():
            shift = days[date[:3]] - today.weekday()
            if shift == 0:
                shift = 7
            return today + datetime.timedelta(days=shift)
        else:
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d-%m-%Y']:
                try:
                    return datetime.datetime.strptime(date, fmt)
                except ValueError:
                    pass
            for fmt in ['%d/%m', '%d-%m', '%d.%m', '%d-%m']:
                # auto set as nearest date in the future
                try:
                    parsed_date = datetime.datetime.strptime(date, fmt)
                    parsed_date = datetime.datetime(year=today.year, month=parsed_date.month, day=parsed_date.day)
                    if parsed_date < today:
                        return datetime.datetime(year=today.year + 1, month=parsed_date.month, day=parsed_date.day)
                    else:
                        return parsed_date
                except ValueError:
                    pass
    raise exception.WrongDateError


def date_pprinter(date: datetime) -> (str, int):
    """Returns pretty string of date.

    2nd element of returned tuple meaning:
    0 - missed
    1 - not missed
    2 - today
    """

    today = datetime.datetime.today()
    delta = (date.date() - today.date()).days
    if delta == 0:
        return 'today', 2
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if delta == -1:
        return 'yesterday', 1
    elif delta == 1:
        return 'tomorrow', 0
    elif 0 < delta <= 7:
        return days[date.weekday()], 0
    else:
        missed = delta < 0
        if missed:
            return f'{-delta} days ago', 1
        else:
            if date.year != today.year:
                return date.strftime('%d %b %Y'), 0
            else:
                return date.strftime('%d %b'), 0
