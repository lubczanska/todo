# tudu

`tudu` is a simple command line tool with a tui mode for managing your to-do lists

## Installation

#### pip

```console
# pip3 install tudu
```
#### locally

You will need to have `SQLAlchemy` and `plyer` packages installed
```
$ git clone https://github.com/lubczanska/tudu
$ cd tudu
$ python3 tudu.py
```  

## Usage

```console
$ tudu --help

usage: tudu [-h] [--quiet]
               {add,rm,edit,check,uncheck,sticky,ls,show} ...

A simple to-do list app

options:
  -h, --help            show this help message and exit
  --quiet, -q           run tui without triggering notifications

commands:
  {add,rm,edit,check,uncheck,sticky,ls,show}
    add                 add new list or tasks
    rm                  remove list or tasks
    edit                edit list/task details
    check               mark task as completed
    uncheck             mark task as not completed
    sticky              add task to startup list
    ls                  display all tasks in a list in tui mode
    show                display task details

If no command is specified tui mode will be opened. In tui mode
press ':' to enter commands

```
#### EXAMPLES
Add a weekly reminder to water plants by sunday
```console
$ tudu add "My list" "Water plants" --deadline sunday --priority 1 --repeat 7
```
Edit a typo in task name
```console
$ tudu edit "My list" "Task with a tpyo in name" --name "Task with no typo in name"
```
Remove "My list"
```console
$ tudu rm "My list"
```
### TUI mode

##### WARNING
Resizing the terminal may lead to visual bugs, especially when entering characters or viewing help.
In that situation resize the terminal properly

#### Navigation
Use arrow keys or `h` `j` `k` `l` to navigate, `Enter` or `Space` to check tasks and `q` to quit

Other keybindings:
- `:` open the command prompt, that supports all cli commands except `ls` and `show`. Additionally, when executing commands like `add` you can use `.` as name of the currently displayed list or type `help` `--help` or `-h` for tui-specific help
- `a` Start adding a list or a task to the currently displayed list
- `d` Start deleting selected entry
- `e` Start editing selected entry
- `i` Show more information
