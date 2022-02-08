import todo.tui.ui as ui
import curses
import textwrap
import todo.data_controllers as data
import todo.exception as exception
import todo.util as util
import todo.tui.prompt as prompt

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


def display_task(screen, task, verbose, center: bool, color: int):
    """
    Display information about a task
    """
    stdscr = screen.stdscr
    info = util.task_info_str(task)
    note = textwrap.wrap(info[3], width=40) if info[3] else ''
    if center:
        note_len = len(note) + 2 if info[3] else 0
        prio_len = 2 if verbose else 0
        deadline_len = 2 if task.deadline else 0
        x_offset = (screen.w - (len(info[0])+8)) // 2
        y_offset = (screen.h - (2+note_len+prio_len+deadline_len) + 1) // 2
    else:
        x_offset = 2
        y_offset = 1
    stdscr.erase()  # clear the terminal
    stdscr.addstr(y_offset, x_offset, '[')
    if task.done:
        stdscr.addstr(y_offset, x_offset + 1, info[1], curses.color_pair(GREEN))
    else:
        stdscr.addstr(y_offset, x_offset + 1, info[1])
    stdscr.addstr(y_offset, x_offset + 2, ']')
    stdscr.addstr(y_offset, x_offset + 3, f'   {info[0]}', curses.color_pair(color) | curses.A_BOLD)
    if task.deadline:
        if task.done:
            deadline_color = GREEN
        elif info[2][1] == 1:
            deadline_color = RED
        elif info[2][1] == 2:
            deadline_color = YELLOW
        else:
            deadline_color = DEF
        stdscr.addstr(y_offset + 2, x_offset + 2, f'due {info[2][0]}', curses.color_pair(deadline_color))
    if info[3]:
        y_offset += 3
        for note_idx, note_line in enumerate(note):
            stdscr.addstr(y_offset + note_idx, x_offset + 5, note_line)
    if verbose:
        y, x = stdscr.getyx()
        stdscr.addstr(y + 2, x_offset + 1, f'priority: {task.priority}', curses.color_pair(BLUE))
        rep = task.repeat
        if rep:
            stdscr.addstr(y + 3, x_offset + 1, f'repeats every {rep} {util.add_s("day", rep)}', curses.color_pair(BLUE))
    stdscr.refresh()


def run_task(stdscr, task_name: str, list_name: str, center: bool, color: int | None = None):
    """
    Task view main loop
    """
    app = ui.UI('task', list_name, util.get_username())
    screen = ui.Screen(stdscr, app)

    task = data.task_info(task_name, list_name)
    verbose = False
    # get color_pair index
    colors = [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
    color = 0 if color is None else colors[color]

    screen.display_wrapper(display_task, task, verbose, center, color)
    key = screen.stdscr.getch()

    while key != ord('q'):
        if key == ord(' '):
            data.edit_task(task_name, list_name, {'done': not task.done})
        elif key == ord('i'):
            # display information about priority and repeating
            verbose = not verbose
        elif key == ord('d'):
            screen.display_wrapper(prompt.error_prompt, 'Delete task? [y/N]')
            key = screen.stdscr.getch()
            if key == ord('y'):
                data.remove_task(task_name, list_name)
                return
        elif key == curses.KEY_RESIZE:
            # handle window resize
            screen.resize()
        task = data.task_info(task_name, list_name)
        screen.display_wrapper(display_task, task, verbose, center, color)
        key = screen.stdscr.getch()
