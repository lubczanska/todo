import curses

from todo.data_manager import list_info, task_info, edit_task,\
    add_task, add_list, rename_list, remove_task, rename_list, count_done,\
    check, session_quit


def print_list(stdscr, list_name, tasks, done, selected_row):
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    x_offset = 5
    y_offset = 2
    stdscr.addstr(y_offset, x_offset, f'{list_name}  [{done}/{len(tasks)}]  {selected_row}', curses.A_BOLD)
    for idx, task in enumerate(tasks):
        info = task_info_str(task)
        x = x_offset
        y = y_offset + 3 + idx
        note_indicator = '*' if info[3] else ' '
        line = f'[{info[1]}] {info[0]}   {info[2]}  {note_indicator}'
        if idx == selected_row:
            stdscr.addstr(y, x, line, curses.color_pair(1))
        else:
            stdscr.addstr(y, x, line)
    stdscr.refresh()


def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w // 2 - len(text) // 2
    y = h // 2
    stdscr.addstr(y, x, text)
    stdscr.refresh()


# ✓
def display_main(stdscr):
    stdscr.clear()

    # turn off cursor blinking
    curses.curs_set(0)
    x_offset = 5
    y_offset = 5

    key = 0
    while key != ord('q'):
        stdscr.refresh()

        key = stdscr.getch()
    session_quit()


def display_list(stdscr, list_name: str):
    stdscr.clear()
    tasks = list_info(list_name)
    done = count_done(list_name)
    length = len(tasks)
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    current_row = 0
    key = 0
    # print the list
    print_list(stdscr, list_name, tasks, done, current_row)

    while key != ord('q'):
        key = stdscr.getch()
        tasks = list_info(list_name)
        done = count_done(list_name)
        length = len(tasks)

        if key == curses.KEY_UP:
            current_row -= 1
            current_row %= length
        elif key == curses.KEY_DOWN:
            current_row += 1
            current_row %= length
        elif key == curses.KEY_ENTER or key in [10, 13]:
            task = tasks[current_row]
            task.done = not task.done
            done = done+1 if task.done else done-1
            edit_task(task.name, list_name, {'done': task.done})
            # check(row[0], list_name, row[1])
        print_list(stdscr, list_name, tasks, done, current_row)
    session_quit()


def task_info_str(task):
    done = '✓' if task.done else ' '
    deadline = f'{task.deadline}' if task.deadline else ''  # TODO pretty printer
    notes = task.notes if task.notes else ''
    return task.name, done, deadline, notes, task.priority


def display_task(stdscr, task_name, list_name):
    task = task_info(task_name, list_name)
    info = task_info_str(task)
    stdscr.clear()

    # turn off cursor blinking
    curses.curs_set(0)
    x_offset = 5
    y_offset = 5

    key = 0
    while key != ord('q'):
        stdscr.refresh()

        stdscr.addstr(y_offset, x_offset, f'{task_name} [{info[1]}]', curses.A_BOLD)
        stdscr.addstr(y_offset+2, x_offset, f'DEADLINE: {info[2]}')
        stdscr.addstr(y_offset+3, x_offset, f'NOTES: {info[3]}')
        stdscr.refresh()
        key = stdscr.getch()
    session_quit()


# ------ controllers --------
def show_main():
    stdscr = curses.initscr()
    curses.wrapper(display_main)


def show_list(list_name):
    stdscr = curses.initscr()
    curses.wrapper(display_list, list_name)


def show_task(task_name, list_name):
    stdscr = curses.initscr()
    curses.wrapper(display_task, task_name, list_name)


