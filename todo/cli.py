import argparse
from todo.data_manager import add_list, add_task, remove_task, remove_list, edit_task, list_list, rename_list, list_info
from todo.tui import show_list, show_task, show_main
parser = argparse.ArgumentParser(description='simple to-do list')
subparser = parser.add_subparsers(dest='command')

# TODO add help to commands

# commands
add = subparser.add_parser('add', help='add a new task or list')
rm = subparser.add_parser('rm', help='remove tasks or lists')
edit = subparser.add_parser('edit', help='edit task/list details')
check = subparser.add_parser('check', help='mark task as completed')
uncheck = subparser.add_parser('uncheck', help='mark task as not completed')
ls = subparser.add_parser('ls', help='list all tasks in a list')
show = subparser.add_parser('show', help='displays task details')


# add
def parse_add(args):
    if not args.TASKS:
        add_list(args.LIST)
    else:
        deadline = args.deadline if args.deadline else None
        priority = args.priority if args.priority else 0
        notes = args.notes if args.notes else None
        for task in args.TASKS:
            add_task(task, args.LIST, deadline, priority, notes)


add.add_argument('LIST', type=str, help='list name')
add.add_argument('TASKS', type=str, nargs='*',
                 help='names of tasks to be added. If empty a new list will be added instead')
add.add_argument('--deadline', type=str)
add.add_argument('--priority', type=int)
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
        changes = {arg: args_vars[arg] for arg in ['name', 'list', 'deadline', 'priority', 'notes'] if args_vars[arg]}
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
        if args.txt:
            for item in list_list():
                print(item)
        else:
        # TODO: display function here
            raise 'Not implemented'
    else:
        if args.txt:
            for item in list_info(args.LIST[0]):
                print(item)
        else:
            show_list(args.LIST[0])


ls.add_argument('LIST', type=str, nargs='*')
ls.add_argument('--txt')
ls.set_defaults(func=parse_ls)


# show
def parse_show(args):
    show_task(args.TASK, args.LIST)


show.add_argument('LIST', type=str)
show.add_argument('TASK', type=str)
show.set_defaults(func=parse_show)

args = parser.parse_args()
# print(args)
if args.command:
    args.func(args)
else:
    show_main()
