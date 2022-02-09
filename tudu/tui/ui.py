""" Screen and UI classes, functions handling displaying main and list mode """

import curses

import tudu.data_controllers as data
import tudu.util as util

DEF = 0
BLACK = 1
RED = 2
GREEN = 3
YELLOW = 4
BLUE = 5
MAGENTA = 6
CYAN = 7
WHITE = 8
HIGH = 9


class Screen:
    """ Main terminal window class """

    def __init__(self, stdscr, app):
        self.stdscr = stdscr  # window object created by curses.initscr()
        self.h, self.w = self.stdscr.getmaxyx()  # terminal window dimensions
        self.app = app  # UI class object
        self.prompt_history = ''  # last prompt entry
        setup_curses()

    def resize(self):
        """ Resize terminal and redraw window content """
        self.h, self.w = self.stdscr.getmaxyx()
        if curses.is_term_resized(self.h, self.w):
            curses.resizeterm(self.h, self.w)
            self.stdscr.clear()
            self.stdscr.refresh()
            self.display_wrapper(self.app.redraw)

    def clear_prompt(self):
        """ Clear the prompt area """
        self.stdscr.move(self.h - 1, 0)
        self.stdscr.clrtoeol()
        self.app.prompt = None
        self.stdscr.refresh()

    def prompt(self, x, message, attr=None):
        """Print text in the prompt area

        Called only from the prompt module

        :param x: x coordinate of message start
        :param message: text to be displayed
        :param attr: styling attributes
        """

        try:
            if attr is None:
                self.stdscr.addstr(self.h - 1, x + 1, message)
            else:
                self.stdscr.addstr(self.h - 1, x + 1, message, attr)
            self.app.prompt = x, message, attr
        except Exception:
            self.stdscr.addstr(self.h - 1, 2, '!')
        finally:
            self.stdscr.refresh()

    def display_wrapper(self, func, *args, **kwargs):
        """ Run a function displaying something on the screen and catch all exceptions"""
        try:
            return func(self, *args, **kwargs)
        except Exception:
            self.too_small()

    def too_small(self):
        """ Window is too small to print necessary content """
        self.stdscr.erase()
        self.stdscr.refresh()


def setup_curses():
    """ Initial setup of the curses library """
    curses.curs_set(0)  # turn off cursor blinking
    curses.noecho()  # don't display key presses
    curses.use_default_colors()  # if the terminal doesn't support 256 color mode problems may arise
    # 1-8 system colors on default background
    # 0 - terminal default
    # 9 - black on white
    curses.init_pair(1, curses.COLOR_BLACK, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)  # missed deadline
    curses.init_pair(3, curses.COLOR_GREEN, -1)  # completed tasks
    curses.init_pair(4, curses.COLOR_YELLOW, -1)  # deadline today
    curses.init_pair(5, curses.COLOR_BLUE, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)
    curses.init_pair(7, curses.COLOR_CYAN, -1)
    curses.init_pair(8, curses.COLOR_WHITE, -1)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)


def print_list_row(stdscr, task, y, x, max_name, verbose=False, color=DEF):
    """ Print one menu entry in list mode

    :param task: Task model object
    :param y: y coordinate
    :param x: x coordinate
    :param max_name: Length of the longest entry
    :param verbose: If True show priority and repeat information
    :param color: Color of the text (default/highlight)
    """

    color2 = GREEN if color == DEF else HIGH
    item = util.task_info_str(task)
    line = f']  {item[0]:<{max_name}}'
    checkbox_l = '['
    # [ ] task_name
    stdscr.addstr(y, x, checkbox_l, curses.color_pair(color))
    stdscr.addstr(y, x + 1, item[1], curses.color_pair(color2))
    stdscr.addstr(y, x + 2, line, curses.color_pair(color))
    # deadline
    if task.done:  # done
        deadline_color = GREEN
    elif item[2][1] == 1:  # missed
        deadline_color = RED
    elif item[2][1] == 2:  # today
        deadline_color = YELLOW
    else:
        deadline_color = DEF
    stdscr.addstr(y, x + max_name + 15, f'{item[2][0]:<9}', curses.color_pair(deadline_color))

    if verbose:
        # notes
        if item[3]:
            stdscr.addstr(y + 1, x + 7, item[3][:70])
        # display info about priority and repeating
        stdscr.addstr(y + 2, x + 1, f'priority: {task.priority}', curses.color_pair(BLUE))
        rep = task.repeat
        if rep is not None:
            stdscr.addstr(y + 2, x + 12,
                          f'        repeats every {rep} {util.add_s("day", rep)}', curses.color_pair(BLUE))
    return y


def print_menu_row(stdscr, item, y, x, max_name, color=DEF):
    """ Print one menu entry in main mode

    :param item: Array of list username, # of tasks, # of completed tasks
    :param y: y coordinate
    :param x: x coordinate
    :param max_name: Length of the longest entry
    :param color: Color of the text (default/highlight)
    """

    line = f'{item[0]:<{max_name}}  [{item[2]}/{item[1]}]'
    stdscr.addstr(y, x, line, curses.color_pair(color))


class UI:
    """ Class for managing tui display in main and list modes """

    def __init__(self, mode: str, list_name: str, username: str):
        self.menu_title = None  # text to be displayed above menu
        self.items_length = 0  # # of entries in menu
        self.items = None  # menu entries
        self.task_summary = None  # task missed, due today or this week tuple
        self.prompt = None  # contents of the prompt area

        self.mode = mode  # main/list/listv
        self.list_name = list_name  # username of the list for list mode
        self.modified = True  # True if db may have been modified
        self.name = username  # Name of user to be displayed in welcome message
        self.current_row = 0  # highlighted row
        self.update_data()
        self.list_finished = False  # True if last task on the list has just been checked

    def get_items(self):
        """
        Fetches data about menu from the database
        Called by update_data and when switching mode
        """
        if self.mode == 'main':
            self.items = data.lists_info()
            self.items_length = len(self.items)
            self.menu_title = f'and you have {self.items_length} to-do {util.add_s("list", self.items_length)}:'
        else:  # elif mode == 'list':
            self.items = data.list_info(self.list_name)
            self.items_length = len(self.items)
            done = data.count_done(self.list_name)
            self.menu_title = f'{self.list_name}   [{done}/{self.items_length}]'
        if self.current_row >= self.items_length > 0:
            self.current_row = self.items_length - 1

    def update_data(self):
        """ If the database has been modified fetch welcome message and menu data """
        if self.modified:
            self.task_summary = data.welcome_tasks()
            self.get_items()
            self.modified = False

    def welcome_message(self, screen: Screen):
        """ Print the totally encouraging welcome message """

        def is_too_much(x):
            return f'{x:>2}' if x <= 99 else 'a lot of'

        x_offset = 3
        y_offset = 2
        stdscr = screen.stdscr
        stdscr.addstr(y_offset - 1, x_offset - 1, f'Hello {self.name}!', curses.A_BOLD)
        stdscr.addstr(y_offset + 1, x_offset, f'you have:   ')
        words1 = ['missed',
                  f'{util.add_s("task", self.task_summary[1])} due ',
                  f'{util.add_s("task", self.task_summary[2])} due ']
        words2 = [f' {util.add_s("task", self.task_summary[0])}', 'today', 'next week']
        for n, word1, word2, color1, color2 in zip(self.task_summary, words1, words2,
                                                   [RED, DEF, DEF], [DEF, YELLOW, DEF]):
            y_offset += 1
            stdscr.addstr(y_offset, x_offset + 12, f'{is_too_much(n)} ')
            y, x = stdscr.getyx()
            stdscr.addstr(y, x, word1, curses.color_pair(color1))
            y, x = stdscr.getyx()
            stdscr.addstr(y, x, word2, curses.color_pair(color2))
        stdscr.refresh()

    def display_main(self, screen: Screen):
        """ Main display function """

        x_offset = 3
        y_offset = 7
        screen.stdscr.addstr(y_offset, x_offset, self.menu_title, curses.A_BOLD)
        # determine how many entries will fit on screen
        if self.items:
            window_height = screen.h - 10
            line_height = 3 if self.mode == 'listv' else 1
            start_idx = 0
            end_idx = window_height // line_height - 2
            if self.current_row > end_idx:
                start_idx, end_idx = self.current_row - end_idx, self.current_row
            y = y_offset + 2
            x = x_offset

            if self.mode == 'main':
                max_name = max(max((len(item[0]) for item in self.items)), 30)
                for idx, item in enumerate(self.items[start_idx:end_idx + 1]):
                    if idx + start_idx == self.current_row:
                        print_menu_row(screen.stdscr, item, y, x, max_name, HIGH)
                    else:
                        print_menu_row(screen.stdscr, item, y, x, max_name, )
                    y += line_height
            else:
                max_name = max(max((len(item.name) for item in self.items)) + 1, 30)
                verbose = self.mode == 'listv'
                for idx, item in enumerate(self.items[start_idx:end_idx + 1]):
                    if idx + start_idx == self.current_row:
                        print_list_row(screen.stdscr, item, y, x, max_name, verbose, HIGH)
                    else:
                        print_list_row(screen.stdscr, item, y, x, max_name, verbose)
                    y += line_height
        screen.stdscr.refresh()

    def redraw(self, screen):
        """ Redraw menu contents """
        screen.stdscr.erase()
        self.update_data()
        self.display_main(screen)
        self.welcome_message(screen)
        if self.prompt:
            screen.prompt(*self.prompt)
            self.prompt = None

    # Utility functions
    def go_up(self):
        if self.items_length:
            self.current_row -= 1
            self.current_row %= self.items_length

    def go_down(self):
        if self.items_length:
            self.current_row += 1
            self.current_row %= self.items_length

    def go_right(self):
        if self.mode == 'main' and self.items_length:
            self.mode = 'list'
            self.list_name = self.items[self.current_row][0]
            self.current_row = 0
            self.get_items()

    def go_left(self):
        if self.mode != 'main':
            self.mode = 'main'
            self.current_row = 0
            self.get_items()

    def toggle_v_mode(self):
        if self.mode == 'list':
            self.mode = 'listv'
        elif self.mode == 'listv':
            self.mode = 'list'

    def check_task(self):
        if self.mode != 'main':
            task = self.items[self.current_row]
            task.done = not task.done
            data.edit_task(task.name, self.list_name, {'done': task.done})
            if self.items_length == data.count_done(self.list_name):
                self.list_finished = True
            self.modified = True
        return

    def delete_entry(self):
        if self.mode == 'main':
            data.remove_list(self.get_selected())
        else:
            data.remove_task(self.get_selected(), self.list_name)
        self.modified = True

    def get_selected(self):
        """ Returns name of selected entry"""
        if self.mode == 'main':
            return self.items[self.current_row][0]
        else:
            return self.items[self.current_row].name
