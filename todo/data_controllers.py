from todo.model import Task, List
from todo import session
import todo.util as util
import todo.exception as exception


def add_task(task_name: str, list_name: str, deadline=None, priority=0, notes=None, repeat=None):
    list_id = session.query(List.id).filter_by(name=list_name).first()
    if list_id is not None:
        if session.query(Task).join(List).filter(Task.name == task_name, List.name == list_name).first() is not None:
            raise exception.DuplicateTaskError
            return
        lst = session.query(List).filter(List.name == list_name).first()
    else:
        lst = List(list_name)
        session.add(lst)
    new_task = Task(task_name, deadline, priority, notes, repeat)
    notify = None
    if priority == 3:
        notify = util.date_add_days(0)
    elif priority == 2:
        notify = util.date_add_days(-7, deadline)
    elif priority == 1:
        notify = util.date_add_days(-1, deadline)
    elif deadline:
        notify = util.date_add_days(1, deadline)
    new_task.notify = notify
    lst.tasks.append(new_task)
    session.add(new_task)
    session.commit()


def add_list(list_name: str):
    if session.query(List.id).filter_by(name=list_name).first() is not None:
        raise exception.DuplicateListError
        return
    new_list = List(list_name)
    session.add(new_list)
    session.commit()


def remove_task(task_name: str, list_name: str):
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    session.query(Task).filter(Task.list == lst.id, Task.name == task_name).delete()
    session.commit()


def remove_list(list_name: str):
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    session.query(Task).filter(Task.list == lst.id).delete()
    session.query(List).filter(List.name == list_name).delete()
    session.commit()


def edit_task(task_name: str, list_name: str, changes):
    task = session.query(Task).join(List).filter(List.name == list_name, Task.name == task_name).first()
    if task is None:
        raise exception.NoTaskError
    for (key, value) in changes.items():
        task[key] = value
    session.commit()


def rename_list(list_name: str, new_name: str):
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    lst.name = new_name
    session.commit()


def lists_info():
    lists = session.query(List).all()
    info = [(lst.name, len(lst.tasks), count_done(lst.name)) for lst in lists]
    return info


def list_info(list_name: str):
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    tasks = session.query(Task).filter(Task.list == lst.id).all()
    return list(tasks)


def task_info(task_name: str, list_name: str):
    task = session.query(Task).join(List).filter(List.name == list_name, Task.name == task_name).first()
    if task is None:
        raise exception.NoTaskError
    return task


def count_done(list_name: str):
    count = session.query(Task).join(List).filter(Task.done, List.name == list_name).count()
    return count


def session_quit():
    session.close()


def manage_deadlines():
    """
    create lists of missed tasks and tasks requiring notification
    and move deadline of all missed repeating tasks
    :return:
    """
    tasks = session.query(Task).all()
    missed = []  # tasks with deadlines missed since last time
    notify = []  # tuples of tasks with due notifications and days left until deadline
    for task in tasks:
        if util.time_to_notify(task.notify):
            left = util.time_to_deadline(task.deadline)
            if left < 0:
                if task.repeat:
                    # repeating tasks are edited to move the deadline and uncheck them
                    task.deadline = util.date_add_days(task.repeat, task.deadline)
                    task.notify = util.calculate_notification(task)
                    task.done = False
                    missed.append(task)
                    if not util.time_to_notify(task.notify):
                        # important or daily repeated tasks might still need a notification
                        continue
                else:
                    task.notify = None
                    if not task.done:
                        missed.append(task)
                    continue
            notify.append((task, left))
            if task.priority == 2:
                task.priority = 1
                task.notify = util.date_add_days(-1, task.deadline)
            if task.priority == 3:
                task.notify = util.date_add_days(0)  # next open TODO: tomorrow
            else:
                task.notify = util.date_add_days(1, task.deadline)
    session.commit()
    return missed, notify
