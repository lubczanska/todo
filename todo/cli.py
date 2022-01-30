import argparse
import shlex

import todo.exception as exception
import todo.tui.tui as tui
from todo.data_controllers import add_list, add_task, remove_task, remove_list, edit_task, lists_info, rename_list
from todo.startup import startup
from todo.util import date_parser

master_parser = argparse.ArgumentParser(add_help=False)
subparser = master_parser.add_subparsers(dest='command')

# TODO add help to commands

# commands
add = subparser.add_parser('add', help='add new list or tasks')
rm = subparser.add_parser('rm', help='remove list or tasks')
edit = subparser.add_parser('edit', help='edit list/task details')
check = subparser.add_parser('check', help='mark task as completed')
uncheck = subparser.add_parser('uncheck', help='mark task as not completed')
ls = subparser.add_parser('ls', help='list all tasks in a list')
show = subparser.add_parser('show', help='display task details')


# add
def parse_add(args):
    if not args.TASKS:
        add_list(args.LIST)
    else:
        deadline = date_parser(args.deadline) if args.deadline else None
        priority = args.priority if args.priority else 0
        if (priority > 0 and deadline is None) or priority not in [0, 1, 2, 3]:
            raise exception.PriorityError
        repeat = args.repeat if args.repeat else None
        notes = args.notes if args.notes else None
        for task in args.TASKS:
            add_task(task, args.LIST, deadline, priority, notes, repeat)


add.add_argument('LIST', type=str, help='list name')
add.add_argument('TASKS', type=str, nargs='*',
                 help='names of tasks to be added. If empty a new list will be added instead')
add.add_argument('--deadline', type=str)
add.add_argument('--priority', type=int)
add.add_argument('--repeat', type=int)
add.add_argument('--notes', type=str)
add.set_defaults(func=parse_add)


# rm
def parse_rm(args):
    if not args.TASKS:
        remove_list(args.LIST)
    else:
        for task in args.TASKS:
            remove_task(task, args.LIST)


rm.add_argument('LIST', type=str)
rm.add_argument('TASKS', type=str, nargs='*')
rm.set_defaults(func=parse_rm)


# edit
def parse_edit(args):
    if not args.TASKS:
        rename_list(args.LIST, args.name)
    else:
        args_vars = vars(args)
        changes = {arg: args_vars[arg] for arg in ['name', 'list', 'priority', 'notes'] if args_vars[arg]}
        changes['deadline'] = date_parser(args.deadline) if args.deadline else None
        for task in args.TASKS:
            edit_task(task, args.LIST, changes)


edit.add_argument('LIST', type=str)
edit.add_argument('TASKS', type=str, nargs='*')
edit.add_argument('--name', type=str)
edit.add_argument('--list', type=str)
edit.add_argument('--deadline', type=str)
edit.add_argument('--priority', type=int)
edit.add_argument('--notes', type=str)
edit.set_defaults(func=parse_edit)


# check
def parse_check(args):
    for task in args.TASKS:
        edit_task(task, args.LIST, {'done': True})


check.add_argument('LIST', type=str)
check.add_argument('TASKS', type=str, nargs='+')
check.set_defaults(func=parse_check)


# uncheck
def parse_uncheck(args):
    for task in args.TASKS:
        edit_task(task, args.LIST, {'done': False})


uncheck.add_argument('LIST', type=str)
uncheck.add_argument('TASKS', type=str, nargs='+')
uncheck.set_defaults(func=parse_uncheck)


# ls
def parse_ls(args):
    if not args.LIST:
        for item in lists_info():  # returns name, # of tasks tuple
            print(item[0])
    else:
        tui.run('list', args.LIST)


ls.add_argument('LIST', type=str, nargs='?')
ls.set_defaults(func=parse_ls)


# show
def parse_show(args):
    tui.run('task', args.LIST, args.TASK)


show.add_argument('LIST', type=str)
show.add_argument('TASK', type=str)
show.set_defaults(func=parse_show)


cli_parser = argparse.ArgumentParser(description='A simple to-do list app',
                                     epilog='If no command is specified tui mode will be opened.\n',
                                     parents=[master_parser])
tui_parser = argparse.ArgumentParser(parents=[master_parser], exit_on_error=False)


def get_help(command=None) -> str:
    if command is None:
        return cli_parser.format_help()
    elif command == 'add':
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
        except exception.DuplicateTaskError:
            print('There is already a task with this name on the list')
        except exception.DuplicateListError:
            print('There is already a list with this name')
        except exception.NoTaskError:
            print("This task or list doesn't exist")
        except exception.WrongDateError:
            print("A date must be on of these things: 'today','tomorrow', day of the week, date in dd/mm/yyyy format")
        except exception.PriorityError:
            print('Priority needs to be an integer between 0 and 3. Priority > 0 needs a deadline')
    else:
        startup()
        tui.run()


def tui_controller(text):
    try:
        args = tui_parser.parse_args(shlex.split(text))
        if args.command in [None, 'ls', 'show']:
            raise exception.IllegalCommandError
        else:
            try:
                args.func(args)
            except Exception:
                raise
    except Exception:
        raise
