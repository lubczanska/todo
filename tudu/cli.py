#!/usr/bin/env python3
""" Parsing cli and tui command arguments, main and tui controller functions """
import argparse
import shlex

import tudu.data_controllers as data
import tudu.exception as exception
import tudu.startup as startup
import tudu.tui.tui as tui
import tudu.util as util


class NoHelpParser(argparse.ArgumentParser):
    """ ArgumentParser that doesn't automatically print help message on error """

    def error(self, message: str):
        raise ValueError(message)


tui_parser = NoHelpParser(add_help=False, exit_on_error=False, prog="")
tui_subparser = tui_parser.add_subparsers(dest='command', title='commands', parser_class=NoHelpParser)

cli_parser = argparse.ArgumentParser(description='A simple app for managing your to-do lists',
                                     epilog="Try <command> -h for additional help. "
                                            "If no command is specified tui mode will be opened. "
                                            "In tui mode press ':' to enter commands")
cli_parser.add_argument('--quiet', '-q', action='store_true',
                        help='Run tui without triggering notifications')
# cli_parser.add_argument('--debug', '-d', action='store_true', help='print out database contents')
cli_subparser = cli_parser.add_subparsers(dest='command', title='commands')


# functions called by subparsers
def parse_add(args):
    if not args.TASKS:
        data.add_list(args.LIST)
    else:
        deadline = util.date_parser(args.deadline) if args.deadline else None
        priority = args.priority if args.priority else 0
        repeat = args.repeat if args.repeat else None
        notes = args.notes if args.notes else None
        for task in args.TASKS:
            try:
                data.add_task(task, args.LIST, deadline, notes, repeat, priority)
            except Exception:
                raise


def parse_sticky(args):
    args.LIST = 'startup'
    parse_add(args)


def parse_rm(args):
    if not args.TASKS:
        data.remove_list(args.LIST)
    else:
        for task in args.TASKS:
            data.remove_task(task, args.LIST)


def parse_edit(args):
    if not args.TASKS:
        data.rename_list(args.LIST, args.name)
    else:
        args_vars = vars(args)
        changes = {arg: args_vars[arg] for arg in ['username', 'priority', 'notes', 'repeat'] if args_vars[arg]}
        if args.deadline:
            changes['deadline'] = util.date_parser(args.deadline)
        for task in args.TASKS:
            data.edit_task(task, args.LIST, changes)


def parse_check(args):
    for task in args.TASKS:
        data.edit_task(task, args.LIST, {'done': True})


def parse_uncheck(args):
    for task in args.TASKS:
        data.edit_task(task, args.LIST, {'done': False})


def parse_ls(args):
    if not args.LIST:
        # print names of all lists
        for item in data.lists_info():  # returns name, # of tasks, # of completed tasks tuple
            print(item[0])
    else:
        tui.run('list', args.LIST)


def parse_show(args):
    if not args.TASK:
        # print names of all tasks in list
        for task in data.list_info(args.LIST):
            print(task.name)
    else:
        tui.run('task', args.LIST, args.TASK, args.center, args.color)


def add_subparsers(subparser):
    """ Add common subparsers to parser """
    add = subparser.add_parser('add', exit_on_error=False, help='add new list/tasks')
    rm = subparser.add_parser('rm', exit_on_error=False, help='remove list/tasks')
    edit = subparser.add_parser('edit', exit_on_error=False, help='edit list/task details')
    check = subparser.add_parser('check', exit_on_error=False, help='check task')
    uncheck = subparser.add_parser('uncheck', exit_on_error=False, help='uncheck task')
    sticky = subparser.add_parser('sticky', exit_on_error=False, help='add task to startup list')

    add.add_argument('LIST', type=str,
                     help="username of the list, will be created if it doesn't exist yet")
    add.add_argument('TASKS', type=str, nargs='*',
                     help='names of tasks to be added, if no names are given an empty list will be added')
    add.add_argument('--deadline', type=str,
                     help="possible values: 'today', 'tomorrow', 'yesterday', string with first 3 letters"
                          " matching a day of the week, date in dd/mm/YYYY or dd/mm format (other separators:"
                          " - , . ). If no year is provided then nearest future date is set")
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

    rm.add_argument('LIST', type=str)
    rm.add_argument('TASKS', type=str, nargs='*')
    rm.set_defaults(func=parse_rm)

    edit.add_argument('LIST', type=str,
                      help="username of the list")
    edit.add_argument('TASKS', type=str, nargs='*',
                      help='names of tasks to receive changes, if no names are given the list can be renamed'
                           'and all the other flags are ignored')
    edit.add_argument('--username', type=str,
                      help='new username for list or tasks')
    # edit.add_argument('--list', type=str, help='username of list where tasks should be moved') <- disabled rn
    edit.add_argument('--deadline', type=str,
                      help="possible values: 'today', 'tomorrow', 'yesterday', string with first 3 letters"
                           " matching a day of the week, date in dd/mm/YYYY or dd/mm format (other separators:"
                           " - , . ). If no year is provided then nearest future date is set")
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

    check.add_argument('LIST', type=str)
    check.add_argument('TASKS', type=str, nargs='+')
    check.set_defaults(func=parse_check)

    uncheck.add_argument('LIST', type=str)
    uncheck.add_argument('TASKS', type=str, nargs='+')
    uncheck.set_defaults(func=parse_uncheck)
    sticky.add_argument('TASKS', type=str, nargs='*',
                        help='names of tasks to be added')
    sticky.add_argument('--deadline', type=str,
                        help="possible values: 'today', 'tomorrow', day of the week, date in dd/mm/YYYY format")
    sticky.add_argument('--priority', type=int,
                        help='controls the amount of notifications (if > 0 a deadline is needed):'
                             ' 0) none'
                             ' 1) 1 day before deadline'
                             ' 2) a week before deadline'
                             ' 3) every time the app is opened')
    sticky.add_argument('--repeat', type=int,
                        help='the task will repeat REPEAT days after deadline (deadline needed)')
    sticky.add_argument('--notes', type=str)
    sticky.set_defaults(func=parse_sticky)
    return add, rm, edit, check, uncheck, sticky


tui_add, tui_rm, tui_edit, tui_check, tui_uncheck, tui_sticky = add_subparsers(tui_subparser)
add, rm, edit, check, uncheck, sticky = add_subparsers(cli_subparser)

# subparsers only for cli mode
ls = cli_subparser.add_parser('ls', help='display list in tui mode')
show = cli_subparser.add_parser('show', help='display task details')

ls.add_argument('LIST', type=str, nargs='?',
                help='name of list to display, if no list is given all lists will be printed instead')
ls.set_defaults(func=parse_ls)

show.add_argument('LIST', type=str)
show.add_argument('TASK', type=str, nargs='?',
                  help='name of task to display, if no list is given all task on LIST will be printed instead')
show.add_argument('--center', '-c', action='store_true', help='display task at the center of the terminal')
show.add_argument('--color', '-C', type=int, help='set task color [0-7]')
show.set_defaults(func=parse_show)


def get_help(command=None) -> str:
    """" Return help message for tui help command """
    if command == 'add':
        return tui_add.format_help()
    elif command == 'rm':
        return tui_rm.format_help()
    elif command == 'edit':
        return tui_edit.format_help()
    elif command == 'check':
        return tui_check.format_help()
    elif command == 'uncheck':
        return tui_uncheck.format_help()
    elif command == 'sticky':
        return tui_sticky.format_help()
    elif command == 'ls':
        return "Command unavailable in tui mode"
    elif command == 'show':
        return "Command unavailable in tui mode"
    else:
        return f"{tui_parser.format_help()}\n\n" \
               f"<command> help         additional help about <command>\n" \
               f"<command>              enter assist mode for <command>\n\n" \
               f"Use arrow keys or hjkl to navigate, Enter or Space to check tasks and q to quit\n\n" \
               f"Other keybindings:\n" \
               f":  open the command prompt, you can use `.` as name of the currently displayed list\n" \
               f"a  start adding a list or a task to the currently displayed list\n" \
               f"d  start deleting selected entry\n" \
               f"e  start editing selected entry\n" \
               f"i  show more information"


def get_args(command: str) -> list[tuple[str, str]]:
    """ Return dict of subparser attributes and pretty prompts for them """
    arg_dict = []
    if command == 'add':
        arg_dict = [('', 'List: '),
                    ('', 'Tasks: '),
                    ('--deadline', 'Deadline: '),
                    ('--priority', 'Priority: '),
                    ('--repeat', 'Repeat: '),
                    ('--notes', 'Notes: ')]
    elif command == 'rm':
        arg_dict = [('', 'List:'),
                    ('', 'Tasks:')]
    elif command == 'edit':
        arg_dict = [('', 'List: '),
                    ('', 'Tasks: '),
                    ('--username', 'Name: '),
                    ('--deadline', 'Deadline: '),
                    ('--priority', 'Priority: '),
                    ('--repeat', 'Repeat: '),
                    ('--notes', 'Notes: ')]
    elif command == 'check':
        arg_dict = [('', 'List: '),
                    ('', 'Tasks: ')]
    elif command == 'uncheck':
        arg_dict = [('', 'List: '),
                    ('', 'Tasks: ')]
    elif command == 'sticky':
        arg_dict = [('', 'Tasks: '),
                    ('--deadline', 'Deadline: '),
                    ('--priority', 'Priority: '),
                    ('--repeat', 'Repeat: '),
                    ('--notes', 'Notes: ')]
    return arg_dict


def main():
    """ Parse cli arguments """
    try:
        args = cli_parser.parse_args()
        if args.command:
            args.func(args)
        # elif args.debug:
        #     data.debug()
        else:
            startup.startup(args.quiet)
            tui.run()
    except Exception as e:
        print(str(e))
    finally:
        data.session_quit()


def tui_controller(text, list_name=None):
    """ Manage parsing for tui command mode """
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


if __name__ == '__main__':
    main()
