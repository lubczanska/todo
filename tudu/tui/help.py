"""Generating and displaying help for tui mode"""
import curses

import tudu.cli as cli

HIGH = 9


def gen_help(command):
    if command in ['help', '--help', '-h', None]:
        help_msg = cli.get_help()
    else:
        help_msg = cli.get_help(command)
    return help_msg


def print_help(stdscr, help_msg):
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    try:
        stdscr.addstr(1, 1, help_msg)
    except Exception:
        pass
    finally:
        stdscr.addstr(h - 1, 1, ' press q to exit ', curses.color_pair(HIGH))
        stdscr.refresh()
