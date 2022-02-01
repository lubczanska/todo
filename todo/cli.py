import argparse
import shlex

import todo.exception as exception
import todo.tui.tui as tui
import todo.data_controllers as data
from todo.startup import startup
from todo.util import date_parser

master_parser = argparse.ArgumentParser(add_help=False)
subparser = master_parser.add_subparsers(dest='command', title='commands')


# commands
add = subparser.add_parser('add', exit_on_error=False, help='add new list or tasks')
rm = subparser.add_parser('rm', exit_on_error=False, help='remove list or tasks')
edit = subparser.add_parser('edit', exit_on_error=False, help='edit list/task details')
check = subparser.add_parser('check', exit_on_error=False, help='mark task as completed')
uncheck = subparser.add_parser('uncheck', exit_on_error=False, help='mark task as not completed')
ls = subparser.add_parser('ls', exit_on_error=False, help='display all tasks in a list in tui mode')
show = subparser.add_parser('show', exit_on_error=False, help='display task details')


# add
def parse_add(args):
    if not args.TASKS:
        data.add_list(args.LIST)
    else:
        deadline = date_parser(args.deadline) if args.deadline else None
        priority = args.priority if args.priority else 0
        repeat = args.repeat if args.repeat else None
        notes = args.notes if args.notes else None
        for task in args.TASKS:
            try:
                data.add_task(task, args.LIST, deadline, notes, repeat, priority)
            except Exception:
                raise


add.add_argument('LIST', type=str,
                 help="name of the list, will be created if it doesn't exist yet")
add.add_argument('TASKS', type=str, nargs='*',
                 help='names of tasks to be added, if no names are given an empty list will be added')
add.add_argument('--deadline', type=str,
                 help="possible values: 'today', 'tomorrow', day of the week, date in dd/mm/YYYY format")
add.add_argument('--priority', type=int,
                 help='controls the amount of notifications (if > 0 a deadline is needed):'
                      ' 0) none'
                      ' 1) 1 day before deadline'
                      ' 2) a week before deadline'
                      ' 3) every time the app is opened')
add.add_argument('--repeat', type=int,
                 help='the task will repeat REPEAT days after deadline (deadline needed)')
add.add_argument('--notes', type=str)
add.set_defaults(func=parse_add)


# rm
def parse_rm(args):
    if not args.TASKS:
        data.remove_list(args.LIST)
    else:
        for task in args.TASKS:
            data.remove_task(task, args.LIST)


rm.add_argument('LIST', type=str)
rm.add_argument('TASKS', type=str, nargs='*')
rm.set_defaults(func=parse_rm)


# edit
def parse_edit(args):
    if not args.TASKS:
        data.rename_list(args.LIST, args.name)
    else:
        args_vars = vars(args)
        changes = {arg: args_vars[arg] for arg in ['name', 'list', 'priority', 'notes', 'repeat'] if args_vars[arg]}
        if args.deadline:
            changes['deadline'] = date_parser(args.deadline)
        for task in args.TASKS:
            data.edit_task(task, args.LIST, changes)


edit.add_argument('LIST', type=str,
                  help="name of the list")
edit.add_argument('TASKS', type=str, nargs='*',
                  help='names of tasks to receive changes, if no names are given the list can be renamed'
                       'and all the other flags are ignored')
edit.add_argument('--name', type=str,
                  help='new name for list or tasks')
edit.add_argument('--list', type=str,
                  help='name of list where tasks should be moved')
edit.add_argument('--deadline', type=str,
                  help="possible values: 'today', 'tomorrow', day of the week, date in dd/mm/YYYY format")
edit.add_argument('--priority', type=int,
                  help='controls the amount of notifications (if > 0 a deadline is needed):'
                       ' 0) none'
                       ' 1) 1 day before deadline'
                       ' 2) a week before deadline'
                       ' 3) every time the app is opened')
edit.add_argument('--repeat', type=int,
                  help='the task will repeat REPEAT days after deadline (deadline needed)')
edit.add_argument('--notes', type=str)
edit.set_defaults(func=parse_edit)


# check
def parse_check(args):
    for task in args.TASKS:
        data.edit_task(task, args.LIST, {'done': True})


check.add_argument('LIST', type=str)
check.add_argument('TASKS', type=str, nargs='+')
check.set_defaults(func=parse_check)


# uncheck
def parse_uncheck(args):
    for task in args.TASKS:
        data.edit_task(task, args.LIST, {'done': False})


uncheck.add_argument('LIST', type=str)
uncheck.add_argument('TASKS', type=str, nargs='+')
uncheck.set_defaults(func=parse_uncheck)


# ls
def parse_ls(args):
    if not args.LIST:
        # print names of all lists
        for item in data.lists_info():  # returns name, # of tasks tuple
            print(item[0])
    else:
        tui.run('list', args.LIST)


ls.add_argument('LIST', type=str, nargs='?',
                help='name of list to display, if no list is given all lists will be printed instead')
ls.set_defaults(func=parse_ls)


# show
def parse_show(args):
    if not args.TASK:
        # print names of all tasks in list
        for task in data.list_info(args.LIST):
            print(task.name)
    else:
        tui.run('task', args.LIST, args.TASK)


show.add_argument('LIST', type=str)
show.add_argument('TASK', type=str, nargs='?',
                  help='name of task to display, if no list is given all task on LIST will be printed instead')
show.set_defaults(func=parse_show)


cli_parser = argparse.ArgumentParser(description='A simple to-do list app',
                                     epilog="If no command is specified tui mode will be opened.\n\n"
                                            "In tui mode press ':' to enter commands",
                                     parents=[master_parser])
cli_parser.add_argument('--quiet', '-q', action='store_true',
                        help='run tui without triggering notifications')
tui_parser = argparse.ArgumentParser(parents=[master_parser], exit_on_error=False, add_help=False)


def get_help(command=None) -> str:
    """"Return help message for tui help command"""
    if command == 'add':
        return add.format_help()
    elif command == 'rm':
        return rm.format_help()
    elif command == 'edit':
        return edit.format_help()
    elif command == 'check':
        return check.format_help()
    elif command == 'uncheck':
        return uncheck.format_help()
    elif command == 'ls':
        return ls.format_help()
    elif command == 'show':
        return show.format_help()
    else:
        return cli_parser.format_help()


def main_controller():
    args = cli_parser.parse_args()
    if args.command:
        try:
            args.func(args)
        except (exception.DuplicateTaskError, exception.DuplicateListError, exception.NoTaskError,
                exception.WrongDateError, exception.PriorityError) as e:
            print(e)
        finally:
            data.session_quit()
    else:
        startup(args.quiet)
        tui.run()
        data.session_quit()


def tui_controller(text, list_name=None):
    try:
        args = tui_parser.parse_args(shlex.split(text))
        if args.command in [None, 'ls', 'show']:
            raise exception.IllegalCommandError
        else:
            if args.LIST == '.' and list_name is not None:
                args.LIST = list_name
            try:
                args.func(args)
            except Exception:
                raise
    except Exception as e:
        raise exception.ParsingError(text, str(e))
