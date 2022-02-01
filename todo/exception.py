class DuplicateTaskError(Exception):
    """Raised when a task with same name and list already exists in the database"""
    def __str__(self):
        return 'There is already a task with this name on the list'


class DuplicateListError(Exception):
    """Raised when a list with same name already exists in the database"""
    def __str__(self):
        return 'There is already a task with this name on the list'


class IllegalCommandError(Exception):
    """Raised when a display command is used in tui mode"""

    def __str__(self):
        return 'Command not allowed in TUI mode'


class WrongDateError(Exception):
    """Raised when the date format is not supported"""

    def __str__(self):
        return "A date must be one of these things: " \
              "'today','tomorrow', day of the week, date in dd/mm/yyyy format"


class NoTaskError(Exception):
    """Raised when the task doesn't exist"""

    def __str__(self):
        return "This task or list doesn't exist"


class PriorityError(Exception):
    """Raised when the priority is not 0-3 or a priority is set with no deadline"""

    def __str__(self):
        return 'Priority needs to be an integer between 0 and 3. Priority > 0 needs a deadline'


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
