import curses
import os
import textwrap

import todo.cli as cli
import todo.exception as exception
import todo.tui.prompt as prompt
import todo.tui.help as help_ui
from todo.data_controllers import list_info, task_info, edit_task, \
    count_done, session_quit, lists_info, remove_list
from todo.util import date_pprinter


def setup_curses():
    curses.curs_set(0)  # turn off cursor blinking
    curses.noecho()  # don't display key presses

    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # menu highlight
    curses.init_pair(2, curses.COLOR_RED, -1)  # missed deadline
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)  # congratulations message


def resize_window(stdscr) -> tuple[int, int]:
    """
    Resize curses window to match current terminal size
    :return: height and width of the terminal
    """
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.refresh()
    return h, w


def task_info_str(task) -> tuple[str, str, tuple[str, bool], str, int]:
    """Format task information for printing"""
    done = '✓' if task.done else ' '
    deadline = date_pprinter(task.deadline) if task.deadline else ('', False)
    notes = task.notes if task.notes else ''
    return task.name, done, deadline, notes, task.priority


def display_main(stdscr, menu_items, menu_title: str, current_row: int, mode: str):
    """
    Displays a menu on the terminal screen
    :param menu_items: list mode: list of tasks, main mode: (name, # of tasks)
    :param menu_title: title above the menu
    :param current_row: row to be highlighted
    :param mode: 'main' or 'list'
    :return:
    """
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    x_offset = 5
    y_offset = 2
    stdscr.addstr(y_offset, x_offset, menu_title, curses.A_BOLD)
    # menu_items:
    # list: {name, list, done, deadline, priority, notes}
    # main: (name, # of tasks)
    if menu_items:
        if mode == 'list':
            max_name = max(max((len(item.name) for item in menu_items)) + 1, 30)
            x = x_offset
            for idx, task in enumerate(menu_items):
                item = task_info_str(task)
                line = f'[{item[1]}]  {item[0]:<{max_name}}'
                y = y_offset + 2 + idx
                if idx == current_row:
                    stdscr.addstr(y, x, line, curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, line)
                if item[2][1]:  # make missed deadlines red
                    stdscr.addstr(y, x + max_name + 15, f'{item[2][0]:<9}', curses.color_pair(2))
                else:
                    stdscr.addstr(y, x + max_name + 15, f'{item[2][0]:<9}')
                if item[3]:
                    note = textwrap.wrap(item[3], width=60)
                    y_offset += len(note)
                    for note_idx, note_line in enumerate(note):
                        stdscr.addstr(y + note_idx + 1, x + 7, note_line)
        else:  # mode == 'main'
            max_name = max((len(item[0]) for item in menu_items))
            for idx, item in enumerate(menu_items):
                line = f'{item[0]:<{max_name}}  [{item[2]}/{item[1]}]'
                x = x_offset
                y = y_offset + 2 + idx
                if idx == current_row:
                    stdscr.addstr(y, x, line, curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, line)
    stdscr.refresh()


def display_task(stdscr, task_name: str, list_name: str):
    """
    Display information about a task until q is pressed
    """
    task = task_info(task_name, list_name)
    info = task_info_str(task)
    key = None
    x_offset = 5
    y_offset = 5
    stdscr.addstr(y_offset, x_offset, f'{task_name} [{info[1]}]', curses.A_BOLD)
    stdscr.addstr(y_offset + 2, x_offset, f'DEADLINE: {info[2]}')
    stdscr.addstr(y_offset + 3, x_offset, f'NOTES: {info[3]}')
    stdscr.refresh()
    while key != ord('q'):
        key = stdscr.getch()


def update_items(mode, list_name):
    if mode == 'main':
        items = lists_info()
        items_length = len(items)
        add_s = '' if items_length == 1 else 'S'
        menu_title = f'YOU HAVE {items_length} TO-DO LIST{add_s}'
    else:  # elif mode == 'list':
        items = list_info(list_name)
        items_length = len(items)
        done = count_done(list_name)
        menu_title = f'{list_name}   [{done}/{items_length}]'
    return items, items_length, menu_title


def handle_commandline(prompt_window, main_window):
    """
    Display command prompt then read and parse user input
    """
    try:
        user_input = prompt.print_prompt(prompt_window).strip()
        if not user_input:
            return
        if user_input.endswith('help') or user_input.endswith('-h'):
            # catches -h, --help and help
            # all commands are single words
            command = user_input.split()[0]
            if command in ['help', '--help', '-h']:
                help_ui.print_help(main_window)
            else:
                help_ui.print_help(main_window, command)
            key = main_window.getch()
            while key != ord('q'):
                key = main_window.getch()
            return
        elif user_input in ['add', 'rm', 'edit', 'check', 'uncheck']:
            user_input = user_input + ' ' + prompt.print_prompt(prompt_window, 'List name:')
        try:
            prompt_window.erase()
            prompt_window.refresh()
            cli.tui_controller(user_input)
        except exception.DuplicateTaskError:
            prompt.error_prompt(prompt_window, 'There is already a task with this name on the list')
        except exception.DuplicateListError:
            prompt.error_prompt(prompt_window, 'There is already a list with this name')
        except exception.NoTaskError:
            prompt.error_prompt(prompt_window, "This task or list doesn't exist")
        except exception.IllegalCommandError:
            prompt.error_prompt(prompt_window, "Command not allowed in TUI mode")
        except exception.WrongDateError:
            prompt.error_prompt(prompt_window,
                                "A date must be one of these things:"
                                "'today','tomorrow', day of the week, date in dd/mm/yyyy format")
        except exception.PriorityError:
            prompt.error_prompt(prompt_window,
                                'Priority needs to be an integer between 0 and 3. Priority > 0 needs a deadline')
        except Exception:
            prompt.error_prompt(prompt_window, f'Command not found: `{user_input}`')
        finally:
            return
    except exception.EscapeKey:
        return


def run_curses(stdscr, mode: str, task_name: str | None, list_name: str | None):
    """
    Main loop
    :param mode: 'main', 'list' or 'task'
    :param task_name: name of task in 'task' mode
    :param list_name: name of list in 'task' and 'list' modes
    """
    stdscr.erase()  # clear the terminal
    setup_curses()  # and set the needed curses settings
    h, w = stdscr.getmaxyx()
    # task mode is just a post-it note style display, you can't switch to a different view
    if mode == 'task':
        display_task(stdscr, task_name, list_name)

    key = None
    current_row = 0
    list_finished = False
    menu_items, menu_length, menu_title = update_items(mode, list_name)

    prompt_window = curses.newwin(1, w, h-1, 0)

    display_main(stdscr, menu_items, menu_title, current_row, mode)
    while key != ord('q'):
        key = stdscr.getch()
        prompt_window.erase()
        prompt_window.refresh()
        if key == curses.KEY_UP:
            # go up 1 row
            current_row -= 1
            current_row %= menu_length
        elif key == curses.KEY_DOWN:
            # go down 1 row
            current_row += 1
            current_row %= menu_length
        elif key == curses.KEY_LEFT and mode == 'list':
            # go back to main menu
            mode = 'main'
            current_row = 0
            menu_items, menu_length, menu_title = update_items(mode, list_name)
        elif key == curses.KEY_RIGHT and mode == 'main' and menu_length > 0:
            # show selected list
            mode = 'list'
            list_name = menu_items[current_row][0]
            current_row = 0
            menu_items, menu_length, menu_title = update_items(mode, list_name)
        elif (key == curses.KEY_ENTER or key in [10, 13]) and menu_length > 0:
            # show selected list/check task
            if mode == 'main':
                mode = 'list'
                list_name = menu_items[current_row][0]
                current_row = 0
                menu_items, menu_length, menu_title = update_items(mode, list_name)
            elif mode == 'list':
                # check item
                task = menu_items[current_row]
                task.done = not task.done
                edit_task(task.name, list_name, {'done': task.done})
                menu_items, menu_length, menu_title = update_items(mode, list_name)
                if menu_length == count_done(list_name):
                    list_finished = True
        elif key == ord(':'):
            # show command prompt and take user input until ESC or ENTER is pressed
            handle_commandline(prompt_window, stdscr)
            menu_items, menu_length, menu_title = update_items(mode, list_name)
        elif key == curses.KEY_RESIZE:
            # handle window resize
            h, w = resize_window(stdscr)
            prompt_window.resize(1, w)
            prompt_window.mvwin(h-1, 0)
        display_main(stdscr, menu_items, menu_title, current_row, mode)
        prompt_window.overlay(stdscr)
        if list_finished:
            #  if the last task has been checked display a congratulations message
            #  and offer to delete the list
            prompt.error_prompt(prompt_window, 'Well done! Would you like to delete this list now?  [y/N]')
            key = stdscr.getch()
            if key == ord('y'):
                remove_list(list_name)
                # go back to main menu
                mode = 'main'
                current_row = 0
                menu_items, menu_length, menu_title = update_items(mode, list_name)
            display_main(stdscr, menu_items, menu_title, current_row, mode)
            list_finished = False
    session_quit()


def run(mode='main', list_name=None, task_name=None):
    os.environ.setdefault("ESCDELAY", "25")
    stdscr = curses.initscr()
    curses.wrapper(run_curses, mode, task_name, list_name)
