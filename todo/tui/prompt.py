import curses

import todo.exception as exception
import todo.tui.tui as tui


def print_prompt(screen, prompt=':'):
    """
    Collect and display text entered by the user.
    Input mode be escaped with ESC and confirmed with ENTER
    :param prompt: prompt to be displayed at the beginning of the line
    :return: text entered by the user
    """
    # the default curses textbox uses some weird emacs keybindings,
    # so I wrote a custom one
    curses.curs_set(True)
    screen.prompt_window.keypad(1)
    screen.prompt_window.erase()
    screen.prompt_window.addstr(0, 0, prompt)
    screen.prompt_window.refresh()
    buffer = ''
    special = [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_BACKSPACE, curses.KEY_DC]
    prompt_len = len(prompt)

    pos = 0
    window = screen.w - prompt_len - 1
    key = screen.prompt_window.get_wch()
    # provide basic editing options
    while key != curses.KEY_ENTER and key not in [10, 13] and key != '\n':
        screen.prompt_window.erase()
        screen.prompt_window.addstr(0, 0, f'{key}')
        if key == curses.KEY_LEFT and pos > 0:
            pos -= 1

        elif key == curses.KEY_RIGHT and pos < len(buffer):
            pos += 1

        elif key == curses.KEY_BACKSPACE and pos > 0:
            buffer = buffer[:pos - 1] + buffer[pos:]
            pos -= 1

        elif key == (curses.KEY_DC or key == 127) and pos < len(buffer):  # DELETE
            buffer = buffer[:pos] + buffer[pos + 1:]

        elif key == curses.KEY_EXIT or key == chr(27):  # ESC
            curses.curs_set(False)
            raise exception.EscapeKey

        elif key in special or type(key) == int:  # so we don't mess up the index
            key = screen.prompt_window.get_wch()
            continue

        elif key == curses.KEY_RESIZE:
            screen.resize()
            # p_w = screen.prompt_window.getmaxyx()[1]
            window = screen.w - prompt_len - 1

        else:
            buffer = buffer[:pos] + screen.key + buffer[pos:]
            pos += 1
        # draw prompt and buffer contents

        screen.prompt_window.erase()
        screen.prompt_window.addstr(0, 0, prompt)
        end_idx = window - prompt_len
        start_idx = 0
        if pos > end_idx:
            start_idx, end_idx = pos - end_idx, pos
        screen.prompt_window.addstr(0, prompt_len, buffer[start_idx:end_idx])
        # move the cursor to correct position
        screen.prompt_window.move(0, pos - start_idx + prompt_len)
        screen.prompt_window.refresh()
        key = screen.prompt_window.get_wch()

    curses.curs_set(False)
    screen.clear_prompt()
    return buffer


def error_prompt(screen, message='error'):
    """
    Display a red text message in the prompt window
    :param message: message to be displayed
    """
    screen.prompt_window.erase()
    screen.prompt_window.attron(curses.A_BOLD)
    screen.prompt_window.addstr(0, 0, message[:screen.w-1], curses.color_pair(2))
    screen.prompt_window.attroff(curses.A_BOLD)
    screen.prompt_window.refresh()


def regular_prompt(screen, message=''):
    """
    Display a white text message in the prompt window
    :param message: message to be displayed
    """
    screen.prompt_window.erase()
    screen.prompt_window.addstr(0, 0, message[:screen.w-1])
    screen.prompt_window.refresh()
