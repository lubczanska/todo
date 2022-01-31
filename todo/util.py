import datetime
import todo.exception as exception


def calculate_notification(task):
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
    """Returns days until date"""
    if date is None:
        return 1000000000  # maybe not the smartest way to do it, but whatever
    today = datetime.datetime.today()
    delta = (date - today).days
    return delta


def time_to_notify(date: datetime) -> bool:
    if not date:
        return False
    today = datetime.datetime.today()
    delta = (date - today).total_seconds()
    return delta < 0


def date_parser(date: str) -> datetime:
    """
    Parse user input date to datetime format
    """
    today = datetime.datetime.today()
    if date == 'today':
        parsed_date = today
    elif date == 'tomorrow':
        parsed_date = today + datetime.timedelta(1)
    else:
        days = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
        if date in days.keys():
            parsed_date = today + datetime.timedelta((days[date]-today.weekday()) % 7)
        else:
            try:
                parsed_date = datetime.datetime.strptime(date, '%d/%m/%Y')
            except Exception:
                raise exception.WrongDateError
    return parsed_date


def date_pprinter(date: datetime) -> (str, int):
    """
    Returns pretty string of date.
    2nd element of returned tuple meaning:
    0 - missed
    1 - not missed
    2 - today
    """
    today = datetime.datetime.today()
    delta = (date - today).days
    if delta == 0:
        return 'today', 2
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if delta == -1:
        return 'yesterday', 1
    elif 0 < delta <= 1:
        return 'tomorrow', 0
    elif 7 >= delta > 0:
        return days[date.weekday()], 0
    else:
        missed = delta < 0
        if missed:
            return f'{-delta} days ago', 1
        else:
            return date.strftime('%d %b %Y'), 0
