# todo

`todo` is a simple command line app with a tui mode for managing your to-do lists

##Installation

coming soon, for now:
```
$ git clone https://github.com/lubczanska/todo

$ cd todo

$ python3 todo.py
```  

##Usage

```bash
$ todo --help

usage: todo [-h] [--quiet] [--debug] {add,rm,edit,check,uncheck,ls,show} ...

A simple to-do list app

options:
  -h, --help            show this help message and exit
  --quiet, -q           run tui without triggering notifications
  --debug, -d           print out db contents

commands:
  {add,rm,edit,check,uncheck,ls,show}
    add                 add new list or tasks
    rm                  remove list or tasks
    edit                edit list/task details
    check               mark task as completed
    uncheck             mark task as not completed
    ls                  display all tasks in a list in tui mode
    show                display task details

If no command is specified tui mode will be opened. In tui mode press ':' to enter commands

```
###TUI mode

- `$ todo` opens the tui in `main` mode
- `$ todo ls LIST` opens the tui in `list` mode, displaying `LIST`
- In tui mode use arrow keys to get around, check and uncheck tasks with enter or space, show details with `i`
 and press `:` to open a command prompt
- `$ todo show LIST TASK` will show a post-it note like task details. Command mode is not available here