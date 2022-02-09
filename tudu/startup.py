""" Managing notification sending and repeating tasks """
from plyer import notification

import tudu.util as util
from tudu.data_controllers import manage_deadlines


def notify_upcoming(task, left: int):
    """ Notify about upcoming deadline """
    deadline = util.date_pprinter(task.deadline)
    text = f'deadline: {deadline[0]}\n' \
           f'{left} {util.add_s("day", left)} left'
    notification.notify(title=task.name, message=text)


def notify_missed(missed_tasks):
    """ Notify about missed deadline """
    text = '\n'.join((task.name for task in missed_tasks))
    notification.notify(title='MISSED TASKS:', message=text)


def startup(quiet=False):
    """ Manage all needed notifications and edit repeating tasks. Called on tui mode startup

    :param quiet: If True no notifications will be sent or modified
    """

    missed, notify = manage_deadlines(quiet)
    if missed:
        notify_missed(missed)
    for task, left in notify:
        notify_upcoming(task, left)
