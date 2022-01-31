class DuplicateTaskError(Exception):
    """Raised when a task with same name and list already exists in the database"""
    pass


class DuplicateListError(Exception):
    """Raised when a list with same name already exists in the database"""
    pass


class IllegalCommandError(Exception):
    """Raised when a display command is used in tui mode"""
    pass


class WrongDateError(Exception):
    """Raised when the date format is not supported"""
    pass


class NoTaskError(Exception):
    """Raised when the task doesn't exist"""
    pass


class PriorityError(Exception):
    """Raised when the priority is not 0-3 or a priority is set with no deadline"""
    pass


class EscapeKey(Exception):
    """Escape key has been pressed. For exiting command input in tui"""
    pass
