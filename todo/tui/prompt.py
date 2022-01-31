import curses

import todo.exception as exception
import todo.tui.tui as tui


def print_prompt(stdscr, prompt=':'):
    """
    Collect and display text entered by the user.
    Input mode be escaped with ESC and confirmed with ENTER
    :param prompt: prompt to be displayed at the beginning of the line
    :return: text entered by the user
    """
    # the default curses textbox uses some weird emacs keybindings,
    # so I wrote a custom one
    h, w = stdscr.getmaxyx()
    curses.curs_set(True)
    stdscr.keypad(1)
    stdscr.erase()
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()
    buffer = ''
    special = [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_BACKSPACE, curses.KEY_DC]
    prompt_len = len(prompt)
    # if buffer is longer than the window we show only part of it,
    # buffer[shift_l:len(buffer)-shift_r]
    pos = 0
    shift_l = 0
    shift_r = 0
    window = w - prompt_len - 1
    key = stdscr.get_wch()
    # provide basic editing options
    while key != curses.KEY_ENTER and key not in [10, 13] and key != '\n':
        if key == curses.KEY_LEFT and pos > 0:
            pos -= 1
            if pos == shift_l - 1:
                shift_l -= 1
                shift_r += 1
        elif key == curses.KEY_RIGHT and pos < len(buffer):
            pos += 1
            if pos == shift_l + window - 1:
                shift_l += 1
                shift_r -= 1
        elif key == curses.KEY_BACKSPACE and pos > 0:
            buffer = buffer[:pos - 1] + buffer[pos:]
            pos -= 1
            if shift_l > 0:
                shift_l -= 1
            else:
                # we only need to do this if the prompt isn't full
                # otherwise it will get printed over anyway
                stdscr.delch(0, pos + prompt_len)
            if pos == shift_l - 1:
                shift_l -= 1
                shift_r += 1

        elif key == (curses.KEY_DC or key == 127) and pos < len(buffer):  # DELETE
            buffer = buffer[:pos] + buffer[pos + 1:]
            if shift_l > 0:
                shift_l -= 1
            else:
                stdscr.delch(0, pos + prompt_len)
        elif key == curses.KEY_EXIT or key == chr(27):  # ESC
            curses.curs_set(False)
            raise exception.EscapeKey
        elif key in special or type(key) == int:  # so we don't mess up the index
            key = stdscr.get_wch()
            continue
        elif key == curses.KEY_RESIZE:
            # handle window resize #TODO: also the main window tho
            h, w = tui.resize_window(stdscr)
        else:
            buffer = buffer[:pos] + key + buffer[pos:]
            pos += 1
            if len(buffer) > window:
                shift_l += 1
            if pos == shift_l + window - 1:
                shift_l += 1
                shift_r -= 1
        # display buffer
        stdscr.addstr(0, prompt_len, buffer[shift_l:len(buffer)-shift_r])
        # move the cursor to desired position
        stdscr.move(0, pos - shift_l + prompt_len)
        stdscr.refresh()
        key = stdscr.get_wch()
    curses.curs_set(False)
    stdscr.refresh()
    return buffer


def error_prompt(stdscr, message='incorrect input, sorry :('):
    """
    Display a red text message in the prompt window
    :param message: message to be displayed
    """
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(0, 0, message, curses.color_pair(2))
    stdscr.attroff(curses.A_BOLD)
    stdscr.refresh()


def regular_prompt(stdscr, message):
    """
    Display a white text message in the prompt window
    :param message: message to be displayed
    """
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, message)
    stdscr.refresh()
