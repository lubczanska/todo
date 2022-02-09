class DuplicateTaskError(Exception):
    """Raised when a task with same username and list already exists in the database"""

    def __str__(self):
        return 'There is already a task with this username on the list'


class DuplicateListError(Exception):
    """Raised when a list with same username already exists in the database"""

    def __str__(self):
        return 'There is already a task with this username on the list'


class IllegalCommandError(Exception):
    """Raised when a display command is used in tui mode"""

    def __str__(self):
        return 'Command not allowed in TUI mode'


class WrongDateError(Exception):
    """Raised when the date format is not supported"""

    def __str__(self):
        return "Invalid date format"


class NoTaskError(Exception):
    """Raised when the task doesn't exist"""

    def __str__(self):
        return "This task or list doesn't exist"


class PriorityError(Exception):
    """Raised when the priority is not 0-3 or a priority is set with no deadline"""

    def __str__(self):
        return 'Priority needs to be an integer between 0 and 3. Priority > 0 requires a deadline'


class ParsingError(Exception):
    """Raised by the parser"""

    def __init__(self, command, message):
        self.command = command
        self.message = message

    def __str__(self):
        if self.message:
            return self.message
        else:
            return f'Command not found: `{self.command}`'


class EscapeKey(Exception):
    """Escape key has been pressed. For exiting command input in tui"""
    pass
