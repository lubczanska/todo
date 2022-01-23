from todo.model import Task, List
from todo import session


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


def list_info(list_name):
    tasks = session.query(Task).join(List).filter(List.name == list_name).all()
    info = [[task.name, task.done, task.deadline, task.priority, task.notes] for task in tasks]
    return info


def task_info(name, lst):
    task = session.query(Task).join(List, Task.list).filter(List.name == lst and Task.name == name).first()
    info = (task.done, task.deadline, task.priority, task.notes)
    return info


def count_done(list_name):
    count = session.query(Task).join(List).filter(List.name == list_name and Task.done).count()
    return count
