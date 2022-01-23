import curses

from todo.data_manager import list_info, task_info, edit_task,\
    add_task, add_list, rename_list, remove_task, rename_list, count_done


def print_list(stdscr, list_name, lst, done, selected_row):
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    x_offset = 20
    y_offset = 2
    stdscr.addstr(y_offset, x_offset, f'{list_name}  [{done}/{len(lst)}]', curses.A_BOLD)
    for idx, (name, done, deadline, priority, notes) in enumerate(lst):
        check = '✓' if done else ' '
        x = x_offset
        y = y_offset + 3 + idx
        note_indicator = '*' if notes else ' '
        print_deadline = f'{deadline}' if deadline else ''
        line = f'[{check}] {name}   {print_deadline}  {note_indicator}'
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

    stdscr.refresh()
    stdscr.getch()


def display_list(stdscr, list_name: str):
    stdscr.clear()
    info = list_info(list_name)
    done = count_done(list_name)
    length = len(info)
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    current_row = 0
    key = 0
    # print the list
    print_list(stdscr, list_name, info, done, current_row)

    while key != ord('q'):
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_row -= 1
            current_row %= length
        elif key == curses.KEY_DOWN:
            current_row += 1
            current_row %= length
        elif key == curses.KEY_ENTER or key in [10, 13]:
            row = info[current_row]
            row[1] = not row[1]
            done = done+1 if row[1] else done-1
            edit_task(row[0], list_name, {'done': row[1]})
        print_list(stdscr, list_name, info, done, current_row)


def display_task(stdscr, name, lst):
    info = task_info(name, lst)
    stdscr.clear()

    stdscr.refresh()
    stdscr.getch()


def show_main():
    stdscr = curses.initscr()
    curses.wrapper(display_main)


def show_list(list_name):
    stdscr = curses.initscr()
    curses.wrapper(display_list, list_name)


def show_task(name, lst):
    stdscr = curses.initscr()
    curses.wrapper(display_task, name, lst)


