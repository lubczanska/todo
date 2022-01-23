from todo.model import Task, List
from todo import session
import datetime


def date_parser(date):
    today = datetime.date.today()
    week_shift = 0
    if date.startswith('next'):
        week_shift = 7
        date = date[5:]
    days = {'monday': 0, 'tuesday': 1, 'friday': 4, 'wednesday': 2, 'thursday': 3, 'saturday': 5, 'sunday': 6}
    parsed_date = today + datetime.timedelta(week_shift + (days[date]-today.weekday()) % 7)
    return parsed_date


def add_task(name, list_name, deadline=None, priority=0, notes=None):
    lst = List(list_name)
    new_task = Task(name, deadline, priority, notes)
    lst.tasks.append(new_task)
    session.add(lst)
    session.add(new_task)
    session.commit()


def add_list(name):
    new_list = List(name)
    session.add(new_list)
    session.commit()


def remove_task(name, lst):
    session.query(Task).join(List).filter(List.name == lst and Task.name == name).delete()
    session.commit()


def remove_list(list_name):
    session.query(Task).join(List).filter(List.name == list_name).delete()
    session.query(List).filter(List.name == list_name).delete()
    session.commit()


def edit_task(name, lst, changes):
    task = session.query(Task).join(List).filter(List.name == lst and Task.name == name).first()
    for (key, value) in changes.items():
        task[key] = value
    session.commit()


def rename_list(list_name, new_name):
    lst = session.query(List).filter(List.name == list_name).first()
    lst.name = new_name
    session.commit()


def list_info(lst_name):
    lst = session.query(List).filter(List.name == lst_name).first()
    tasks = session.query(Task).join(List).filter(List.name == lst_name).all()
    print(f'{lst.name}\n')
    for task in tasks:
        check = '✓' if task.done else ' '
        print(f'[{check}]  {task.name}')


def task_info(name, lst):
    task = session.query(Task).join(List, Task.list).filter(List.name == lst and Task.name == name).first()
    return task

# TODO: all interactions with database
