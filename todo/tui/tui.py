import curses
import os

import todo.cli as cli
import todo.data_controllers as data
import todo.exception as exception
import todo.tui.help as help_ui
import todo.tui.prompt as prompt
import todo.tui.task as task
import todo.tui.ui as ui
import todo.util as util


def command_mode(screen: ui.Screen):
    """
    Display command prompt then read and parse user input;
    display help message if requested or parsing errors
    """
    db_modified = False
    try:
        user_input = prompt.commandline(screen)
        if not user_input:
            curses.curs_set(False)
            return
        user_input = user_input.strip()
        if user_input.endswith('help') or user_input.endswith('-h'):
            # catches -h, --help and help
            # all commands are single words
            command = user_input.split()[0]
            if command in ['help', '--help', '-h']:
                help_ui.print_help(screen.stdscr)
            else:
                help_ui.print_help(screen.stdscr, command)
            key = screen.stdscr.getch()
            while key != ord('q'):
                key = screen.stdscr.getch()
            return
        # TODO: assist mode
        # elif user_input in ['add', 'rm', 'edit', 'check', 'uncheck']:
        #     user_input = user_input + ' ' + prompt.print_prompt(screen, 'List name:')
        try:
            # Try parsing user input, display exceptions in the prompt
            list_name = screen.app.list_name if screen.app.mode != 'main' else None
            cli.tui_controller(user_input, list_name)
            db_modified = True
        except Exception as e:
            prompt.error_prompt(screen, str(e))
        finally:
            return db_modified
    except exception.EscapeKey:
        # ESC has been pressed. Cleanup and exit command mode
        return False


def run_curses(stdscr, mode: str, list_name: str | None):
    """
    Main loop
    """

    app = ui.UI(mode, list_name, util.get_username())
    screen = ui.Screen(stdscr, app)

    screen.display_wrapper(app.redraw)
    key = None
    while key != ord('q'):
        key = screen.stdscr.getch()

        if key == curses.KEY_UP:
            app.go_up()
        elif key == curses.KEY_DOWN:
            app.go_down()
        elif key == curses.KEY_LEFT:
            app.go_left()
        elif key == curses.KEY_RIGHT:
            app.go_right()
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if app.mode == 'main':
                app.go_right()
            else:
                app.check_task()
        elif key == ord(' '):
            app.check_task()
        elif key == ord(':'):
            # show command prompt and take user input until ESC or ENTER is pressed
            if screen.display_wrapper(command_mode):
                # user entered a valid command, modifying the database
                app.modified = True
        elif key == ord('i'):
            app.toggle_v_mode()
        elif key == curses.KEY_RESIZE:
            # handle window resize
            screen.resize()

        screen.display_wrapper(app.redraw)

        if app.list_finished:
            #  if the last task has been checked display a congratulations message
            #  and offer to delete the list
            screen.display_wrapper(prompt.error_prompt, 'Well done! Would you like to delete this list now?  [y/N]')
            key = screen.stdscr.getch()
            if key == ord('y'):
                data.remove_list(app.list_name)
                app.go_left()
                # app.modified != True, because all go_left called app.get_items
                # and all tasks are done, so welcome message won't change
            screen.clear_prompt()
            screen.display_wrapper(app.redraw)
            app.list_finished = False


def run(mode='main', list_name=None, task_name=None):
    os.environ.setdefault("ESCDELAY", "25")
    stdscr = curses.initscr()
    if mode == 'task':
        curses.wrapper(task.run_task, task_name, list_name)
    else:
        curses.wrapper(run_curses, mode, list_name)

