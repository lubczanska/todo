""" Interacting with the database """
from datetime import datetime

import tudu.exception as exception
import tudu.util as util
from tudu import session
from tudu.model import Task, List


def add_task(task_name: str, list_name: str, deadline: datetime | None, notes: str | None,
             repeat: int | None, priority: int = 0):
    """Add new task to the database.

    Raise exception if task with task_name exists on list_name.
    Validate priority
    """

    list_id = session.query(List.id).filter_by(name=list_name).first()
    if list_id is not None:
        if session.query(Task).join(List).filter(Task.name == task_name, List.name == list_name).first() is not None:
            raise exception.DuplicateTaskError
            return
        lst = session.query(List).filter(List.name == list_name).first()
    else:
        lst = List(list_name)
        session.add(lst)
    # assert priority > 0 => a deadline is set
    if priority > 0 and deadline is None:
        raise exception.PriorityError
    new_task = Task(task_name, deadline, priority, notes, repeat)
    # create date of notification
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
    lst.task_ids.append(new_task)
    session.add(new_task)
    session.commit()


def add_list(list_name: str):
    """ Add new list to the database. Check if name is unique """
    if session.query(List.id).filter_by(name=list_name).first() is not None:
        raise exception.DuplicateListError
        return
    if list_name == 'startup':
        raise ValueError("List 'startup' cannot be added")
    new_list = List(list_name)
    session.add(new_list)
    session.commit()


def remove_task(task_name: str, list_name: str):
    """ Check if task exists. If yes, remove from database """
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    session.query(Task).filter(Task.list_id == lst.id, Task.name == task_name).delete()
    session.commit()


def remove_list(list_name: str):
    """ Remove list and its tasks """
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    session.query(Task).filter(Task.list_id == lst.id).delete()
    session.query(List).filter(List.name == list_name).delete()
    session.commit()


def edit_task(task_name: str, list_name: str, changes):
    """ Check if task exists. If yes, edit task details. Validate priority > 0 => deadline exists """
    task = session.query(Task).join(List).filter(List.name == list_name, Task.name == task_name).first()
    if task is None:
        raise exception.NoTaskError
    for (key, value) in changes.items():
        if key == 'username' and session.query(Task).join(List).filter(Task.name == key,
                                                                       List.name == list_name).first() is not None:
            raise exception.DuplicateTaskError
        task[key] = value
    # abort changes if new values are incorrect
    if task.priority > 0 and task.deadline is None:
        raise exception.PriorityError
    session.commit()


def rename_list(list_name: str, new_name: str):
    """ If list exists change its username to new_name """
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    lst.name = new_name
    session.commit()


def lists_info() -> list[tuple[str, int, int]]:
    """ Return info about number of all tasks and completed tasks for each list """
    lists = session.query(List).all()
    info = []
    for lst in lists:
        if lst.name != 'startup' or len(lst.task_ids) > 0:
            info.append((lst.name, len(lst.task_ids), count_done(lst.name)))
    return info


def list_info(list_name: str):
    """ Return information about list if it exists """
    lst = session.query(List).filter(List.name == list_name).first()
    if lst is None:
        raise exception.NoTaskError
    tasks = session.query(Task).filter(Task.list_id == lst.id).all()
    return list(tasks)


def task_info(task_name: str, list_name: str):
    """ Return task if it exists """
    task = session.query(Task).join(List).filter(List.name == list_name, Task.name == task_name).first()
    if task is None:
        raise exception.NoTaskError
    return task


def count_done(list_name: str) -> int:
    """ Count completed tasks on list_name """
    count = session.query(Task).join(List).filter(Task.done, List.name == list_name).count()
    return count


def welcome_tasks() -> tuple[int, int, int]:
    """ Return number of missed tasks and tasks due today and this week """
    tasks = session.query(Task).all()
    missed = 0
    today = 0
    this_week = 0
    for task in tasks:
        if task.done:
            continue
        left = util.time_until_date(task.deadline)
        if left < 0:
            missed += 1
        elif left < 7:
            this_week += 1
            if left == 0:
                today += 1
    return missed, today, this_week


def session_quit():
    session.close()


def manage_deadlines(quiet):
    """ Create lists of missed tasks and tasks requiring notification, move deadlines of all missed repeating tasks

    :param quiet: only repeating tasks are managed, nothing else is modified, nothing is returned
    :return: Lists of missed and due for a notification Task objects
    """

    tasks = session.query(Task).all()
    missed = []  # tasks with deadlines missed since last time
    notify = []  # tuples of tasks with due notifications and days left until deadline
    for task in tasks:
        if util.time_to_notify(task.notify) and task.deadline:
            left = util.time_until_date(task.deadline)
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
                elif not quiet:
                    task.notify = None
                    if not task.done:
                        missed.append(task)
                    continue
            if quiet:
                continue
            notify.append((task, left))
            if task.priority == 2:
                task.priority = 1
                task.notify = util.date_add_days(-1, task.deadline)
            if task.priority == 3:
                task.notify = util.date_add_days(0)
            else:
                task.notify = util.date_add_days(1, task.deadline)
    session.commit()
    return missed, notify


def debug():
    """ Display all items on the database """
    lists = session.query(List).all()
    tasks = session.query(Task).all()
    print('LISTS:')
    for lst in lists:
        print(f'{lst.id:>3}. {lst.name} {lst.task_ids}')
    print('TASKS:')
    for task in tasks:
        print(f'{task.id:>3}. {task.name} {task.list_id} '
              f'{task.done} {task.deadline} {task.priority} {task.notify} '
              f'{task.notes}')
