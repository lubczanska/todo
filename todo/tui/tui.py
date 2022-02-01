import curses
import os
import pwd

import todo.cli as cli
import todo.data_controllers as data
import todo.exception as exception
import todo.tui.help as help_ui
import todo.tui.prompt as prompt
import todo.util as util
import todo.tui.task as task


class Screen:
    def __init__(self, stdscr, create_prompt=True):
        self.main_window = stdscr
        self.h, self.w = self.main_window.getmaxyx()
        self.prompt = create_prompt
        if self.prompt:
            self.prompt_window = curses.newwin(1, self.w, self.h - 1, 0)
        setup_curses()

    def resize(self):
        self.h, self.w = self.main_window.getmaxyx()
        curses.resizeterm(self.h, self.w)
        # self.main_window.clear()
        self.main_window.refresh()

        if self.prompt:
            #del self.prompt_window
            #self.prompt_window = curses.newwin(1, self.w, self.h - 1, 0)
            self.prompt_window.resize(1, self.w)
            self.prompt_window.mvwin(self.h - 1, 0)
            self.prompt_window.refresh()
        return

    def clear_prompt(self):
        self.prompt_window.erase()
        self.prompt_window.refresh()

    def display_wrapper(self, f, *args):
        if self.h < 5 or self.w < 20:
            # self.main_window.erase()
            # self.main_window.refresh()
            self.too_small()
        else:
            try:
                f(self, *args)
                if self.prompt:
                    self.prompt_window.overlay(self.main_window)
            except Exception:
                self.too_small()

    def too_small(self):
        self.main_window.erase()
        #message = 'WINDOW TOO SMALL'
        #self.main_window.addstr(self.h // 2, (self.w - len(message) // 2), message, curses.A_REVERSE + curses.A_BOLD)
        self.main_window.refresh()


def setup_curses():
    curses.curs_set(0)  # turn off cursor blinking
    curses.noecho()  # don't display key presses
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # menu highlight
    curses.init_pair(2, curses.COLOR_RED, -1)  # missed deadline
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # deadline today
    curses.init_pair(4, curses.COLOR_GREEN, -1)  # for completed tasks
    curses.init_pair(5, -1, -1)  # default
    curses.init_pair(6, curses.COLOR_BLUE, -1)  # blue


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def task_info_str(task) -> tuple[str, str, tuple[str, bool], str, int]:
    """Format task information for printing"""
    done = '✓' if task.done else ' '
    deadline = util.date_pprinter(task.deadline) if task.deadline else ('', False)
    notes = task.notes if task.notes else ''
    return task.name, done, deadline, notes, task.priority


def print_menu_row(stdscr, item, y, x, max_name, color=5):
    line = f'{item[0]:<{max_name}}  [{item[2]}/{item[1]}]'
    stdscr.addstr(y, x, line, curses.color_pair(color))


def print_list_row(stdscr, task, y, x, max_name, verbose=False, color=5):
    color2 = 4 if color == 5 else 1

    item = task_info_str(task)
    line = f']  {item[0]:<{max_name}}'
    checkbox_l = '['
    # [ ] task_name
    stdscr.addstr(y, x, checkbox_l, curses.color_pair(color))
    stdscr.addstr(y, x + 1, item[1], curses.color_pair(color2))
    stdscr.addstr(y, x + 2, line, curses.color_pair(color))
    # deadline
    if task.done:  # done tasks green
        stdscr.addstr(y, x + max_name + 15, f'{item[2][0]:<9}', curses.color_pair(4))
    elif item[2][1]:  # missed deadlines red, today yellow
        stdscr.addstr(y, x + max_name + 15, f'{item[2][0]:<9}', curses.color_pair(item[2][1] + 1))
    else:
        stdscr.addstr(y, x + max_name + 15, f'{item[2][0]:<9}')

    if verbose:
        # notes
        if item[3]:
            stdscr.addstr(y + 1, x + 7, item[3][:70])
        # display info about priority and repeating
        stdscr.addstr(y + 2, x + 1, f'priority: {task.priority}', curses.color_pair(6))
        rep = task.repeat
        if rep is not None:
            stdscr.addstr(y + 2, x + 12,
                          f'        repeats every {rep} {util.add_s("day", rep)}', curses.color_pair(6))
    return y


def display_main(screen: Screen, menu_items, menu_title: str, current_row: int, mode: str):
    """
    Displays a menu on the terminal screen
    :param menu_items: list mode: list of tasks, main mode: (name, # of tasks)
    :param menu_title: title above the menu
    :param current_row: row to be highlighted
    :param mode: 'list','listv' or 'main'
    :return:
    """
    stdscr = screen.main_window
    screen.main_window.erase()
    x_offset = 3
    y_offset = 7
    screen.main_window.addstr(y_offset, x_offset, menu_title, curses.A_BOLD)
    # determine how many entries will fit on screen
    if menu_items:

        window_height = screen.h - 10
        line_height = 3 if mode == 'listv' else 1
        start_idx = 0
        end_idx = window_height // line_height - 2
        if current_row > end_idx:
            start_idx, end_idx = current_row - end_idx, current_row
        y = y_offset + 2
        x = x_offset

        if mode == 'main':
            max_name = max((len(item[0]) for item in menu_items))
            for idx, item in enumerate(menu_items[start_idx:end_idx+1]):
                if idx + start_idx == current_row:
                    print_menu_row(stdscr, item, y, x, max_name, 1)
                else:
                    print_menu_row(stdscr, item, y, x, max_name, )
                y += line_height
        else:
            max_name = max(max((len(item.name) for item in menu_items)) + 1, 30)
            verbose = mode == 'listv'
            for idx, item in enumerate(menu_items[start_idx:end_idx+1]):
                if idx + start_idx == current_row:
                    print_list_row(stdscr, item, y, x, max_name, verbose, 1)
                else:
                    print_list_row(stdscr, item, y, x, max_name, verbose)
                y += line_height
    stdscr.refresh()


def update_items(mode, list_name):
    if mode == 'main':
        items = data.lists_info()
        items_length = len(items)
        menu_title = f'and you have {items_length} to-do {util.add_s("list", items_length)}:'
    else:  # elif mode == 'list':
        items = data.list_info(list_name)
        items_length = len(items)
        done = data.count_done(list_name)
        menu_title = f'{list_name}   [{done}/{items_length}]'
    return items, items_length, menu_title


def handle_commandline(screen: Screen):
    """
    Display command prompt then read and parse user input
    """
    try:
        user_input = prompt.print_prompt(screen)
        if not user_input:
            curses.curs_set(False)
            return
        user_input = user_input.strip()
        if user_input.endswith('help') or user_input.endswith('-h'):
            # catches -h, --help and help
            # all commands are single words
            command = user_input.split()[0]
            if command in ['help', '--help', '-h']:
                help_ui.print_help(screen.main_window)
            else:
                help_ui.print_help(screen.main_window, command)
            key = screen.main_window.getch()
            while key != ord('q'):
                key = screen.main_window.getch()
            return
        # elif user_input in ['add', 'rm', 'edit', 'check', 'uncheck']:
        #     user_input = user_input + ' ' + prompt.print_prompt(screen, 'List name:')
        try:
            screen.clear_prompt()
            cli.tui_controller(user_input)
        except (exception.DuplicateTaskError, exception.DuplicateListError, exception.NoTaskError,
                exception.IllegalCommandError, exception.WrongDateError, exception.PriorityError,
                exception.ParsingError) as e:
            prompt.error_prompt(screen, str(e))
        except Exception as e:
            prompt.error_prompt(screen, str(e))
        finally:
            curses.curs_set(False)
            return
    except exception.EscapeKey:
        curses.curs_set(False)
        screen.clear_prompt()
        return


def welcome_message(screen: Screen, tasks_summary: tuple[int, int, int], name: str):
    """Print the totally encouraging welcome message"""
    x_offset = 3
    y_offset = 2
    stdscr = screen.main_window
    stdscr.addstr(y_offset - 1, x_offset - 1, f'Hello {name}!', curses.A_BOLD)
    is_too_much = lambda x: f'{x:>2}' if x <= 99 else 'a lot of'
    stdscr.addstr(y_offset + 1, x_offset, f'you have:   ')
    words1 = ['missed', f'{util.add_s("task", tasks_summary[1])} due ', f'{util.add_s("task", tasks_summary[2])} due ']
    words2 = [f' {util.add_s("task", tasks_summary[0])}', 'today', 'next week']
    for n, word1, word2, color1, color2 in zip(tasks_summary, words1, words2, [2, 5, 5], [5, 3, 5]):
        y_offset += 1
        stdscr.addstr(y_offset, x_offset + 12, f'{is_too_much(n)} ')
        y, x = stdscr.getyx()
        stdscr.addstr(y, x, word1, curses.color_pair(color1))
        y, x = stdscr.getyx()
        stdscr.addstr(y, x, word2, curses.color_pair(color2))
        stdscr.refresh()


def run_curses(stdscr, mode: str, list_name: str | None):
    """
    Main loop
    :param mode: 'main', 'list', 'listv'
    :param list_name: name of list in 'list' modes
    """
    screen = Screen(stdscr)
    current_row = 0
    list_finished = False
    menu_items, menu_length, menu_title = update_items(mode, list_name)
    name = get_username()
    welcome_tasks = data.welcome_tasks()

    screen.display_wrapper(display_main, menu_items, menu_title, current_row, mode)
    screen.display_wrapper(welcome_message, welcome_tasks, name)
    key = None
    while key != ord('q'):
        key = screen.main_window.getch()
        screen.prompt_window.erase()
        screen.prompt_window.refresh()
        if key == curses.KEY_UP:
            # go up 1 row
            current_row -= 1
            current_row %= menu_length
        elif key == curses.KEY_DOWN:
            # go down 1 row
            current_row += 1
            current_row %= menu_length
        elif key == curses.KEY_LEFT and mode != 'main':
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
            elif mode != 'main':
                # check item
                task = menu_items[current_row]
                task.done = not task.done
                data.edit_task(task.name, list_name, {'done': task.done})
                menu_items, menu_length, menu_title = update_items(mode, list_name)
                if menu_length == data.count_done(list_name):
                    list_finished = True
        elif key == ord(':'):
            # show command prompt and take user input until ESC or ENTER is pressed
            screen.display_wrapper(handle_commandline)
            menu_items, menu_length, menu_title = update_items(mode, list_name)
        elif key == ord('i'):
            if mode == 'list':
                mode = 'listv'
            elif mode == 'listv':
                mode = 'list'
        elif key == curses.KEY_RESIZE:
            # handle window resize
            screen.resize()

        screen.display_wrapper(display_main, menu_items, menu_title, current_row, mode)
        welcome_tasks = data.welcome_tasks()
        screen.display_wrapper(welcome_message, welcome_tasks, name)
        #screen.prompt_window.overlay(screen.main_window)
        #screen.prompt_window.refresh()
        if list_finished:
            #  if the last task has been checked display a congratulations message
            #  and offer to delete the list
            screen.display_wrapper(prompt.error_prompt, 'Well done! Would you like to delete this list now?  [y/N]')
            key = screen.main_window.getch()
            if key == ord('y'):
                data.remove_list(list_name)
                # go back to main menu
                mode = 'main'
                current_row = 0
                menu_items, menu_length, menu_title = update_items(mode, list_name)

            screen.display_wrapper(display_main, menu_items, menu_title, current_row, mode)
            screen.display_wrapper(welcome_message, welcome_tasks, name)
            list_finished = False
    data.session_quit()


def run(mode='main', list_name=None, task_name=None):
    os.environ.setdefault("ESCDELAY", "25")
    stdscr = curses.initscr()
    if mode == 'task':
        curses.wrapper(task.run_task, task_name, list_name)
    else:
        curses.wrapper(run_curses, mode, list_name)
