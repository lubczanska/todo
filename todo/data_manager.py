from todo.model import Task, List
from todo import session
# TODO: make get_or_create function and repeated adding blocker


def add_task(name, list_name, deadline=None, priority=0, notes=None):
    list_id = session.query(List.id).filter_by(name=list_name).first()
    if list_id is not None:
        if session.query(Task).join(List).filter(Task.name == name, List.name == list_name).first() is not None:
            print('a task with this name already exists on this list')
            return
        lst = session.query(List).filter(List.name == list_name).first()
    else:
        lst = List(list_name)
        session.add(lst)
    new_task = Task(name, deadline, priority, notes)
    lst.tasks.append(new_task)
    session.add(new_task)
    session.commit()


def add_list(name):
    if session.query(List.id).filter_by(name=name).first() is not None:
        print('a list with this name already exists')
        return
    new_list = List(name)
    session.add(new_list)
    session.commit()


def remove_task(name, lst):
    session.query(Task).join(List).filter(List.name == lst, Task.name == name).delete()
    session.commit()


def remove_list(list_name):
    session.query(Task).join(List).filter(List.name == list_name).delete()
    session.query(List).filter(List.name == list_name).delete()
    session.commit()


def edit_task(name, lst, changes):
    task = session.query(Task).join(List).filter(List.name == lst, Task.name == name).first()
    for (key, value) in changes.items():
        task[key] = value
    session.commit()


def check(name, lst, status):
    task = session.query(Task).join(List).filter(List.name == lst, Task.name == name).first()
    task.done = status
    session.commit()


def rename_list(list_name, new_name):
    lst = session.query(List).filter(List.name == list_name).first()
    lst.name = new_name
    session.commit()


def list_list():
    lists = [l.name for l in session.query(List).all()]
    return lists


def list_info(list_name):
    tasks = session.query(Task).join(List).filter(List.name == list_name).all()
    info = [[task.name, task.done, task.deadline, task.priority, task.notes] for task in tasks]
    return [task for task in tasks]


def task_info(name, lst):
    task = session.query(Task).join(List).filter(List.name == lst, Task.name == name).first()
    info = [task.done, task.deadline, task.priority, task.notes]
    return task


def count_done(list_name):
    count = session.query(Task).join(List).filter(Task.done, List.name == list_name).count()
    return count


def session_quit():
    session.close()
