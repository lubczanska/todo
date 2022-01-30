import curses

import todo.exception as exception
import todo.tui.tui as tui
import todo.cli as cli


def print_help(stdscr, command=None):
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    if command:
        help_msg = cli.get_help(command)
    else:
        help_msg = cli.get_help()
    stdscr.addstr(h-1, 1, ' press q to exit ', curses.color_pair(1))
    stdscr.addstr(2, 1, help_msg)
    stdscr.refresh()


