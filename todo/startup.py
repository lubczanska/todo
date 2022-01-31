from plyer import notification
from todo.data_controllers import manage_deadlines
from todo.util import date_pprinter


def notify_upcoming(task, left: int):
    days = 'days' if left != 1 else 'day'
    text = f'deadline: {date_pprinter(task.deadline)[0]}\n' \
           f'{left} {days} left'
    notification.notify(
        title=task.name,
        message=text)


def notify_missed(missed_tasks):
    text = '\n'.join((task.name for task in missed_tasks))
    notification.notify(
        title='MISSED TASKS:',
        message=text)


def startup(quiet=False):
    """
    Manage all needed notifications and edit repeating tasks. Ran on tui mode startup
    :param quiet: no notifications will be sent or modified
    """
    missed, notify = manage_deadlines(quiet)
    if missed:
        notify_missed(missed)
    for task, left in notify:
        notify_upcoming(task, left)
