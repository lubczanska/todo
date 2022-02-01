import todo.tui.tui as tui
import curses
import textwrap
import todo.data_controllers as data
import todo.exception as exception
import todo.util as util


def display_task(screen, task, verbose):
    """
    Display information about a task
    """
    stdscr = screen.main_window
    info = tui.task_info_str(task)
    x_offset = 2
    y_offset = 2
    stdscr.erase()  # clear the terminal
    stdscr.addstr(y_offset, x_offset, '[]')
    if task.done:
        stdscr.addstr(y_offset, x_offset + 1, info[1], curses.color_pair(4))
    else:
        stdscr.addstr(y_offset, x_offset + 1, info[1])
    stdscr.addstr(y_offset, x_offset + 2, ']')
    stdscr.addstr(y_offset, x_offset + 3, f'   {info[0]}', curses.A_BOLD)
    if info[2][1]:
        stdscr.addstr(y_offset + 2, x_offset + 2, f'due {info[2][0]}', curses.color_pair(info[2][1] + 1))
    else:
        stdscr.addstr(y_offset + 2, x_offset + 2, f'due {info[2][0]}')
    if info[3]:
        note = textwrap.wrap(info[3], width=40)
        y_offset += 3
        for note_idx, note_line in enumerate(note):
            stdscr.addstr(y_offset + note_idx, x_offset + 5, note_line)
    if verbose:
        y, x = stdscr.getyx()
        stdscr.addstr(y + 2, x_offset + 1, f'priority: {task.priority}')
        rep = task.repeat
        if rep:
            stdscr.addstr(y + 3, x_offset + 1, f'repeats every {rep} {util.add_s("day", rep)}')
    stdscr.refresh()


def run_task(stdscr, task_name: str, list_name: str):
    """
    Task view main loop
    """
    screen = tui.Screen(stdscr, False)
    task = data.task_info(task_name, list_name)
    verbose = False
    screen.display_wrapper(display_task, task, verbose)
    key = screen.main_window.getch()
    while key != ord('q'):
        if key == ord(' '):
            data.edit_task(task_name, list_name, {'done': not task.done})
        elif key == ord('i'):
            # diplay info about priority and repeating
            verbose = not verbose
        elif key == curses.KEY_RESIZE:
            # handle window resize
            screen.resize()
        task = data.task_info(task_name, list_name)
        screen.display_wrapper(display_task, task, verbose)
        key = screen.main_window.getch()
