class DuplicateTaskError(Exception):
    """Raised when a task with same name and list already exists in the database"""
    pass


class DuplicateListError(Exception):
    """Raised when a list with same name already exists in the database"""
    pass


class WrongCommandError(Exception):
    pass


class IllegalCommandError(Exception):
    pass


class WrongDateError(Exception):
    pass


class NoTaskError(Exception):
    pass


class PriorityError(Exception):
    pass


class EscapeKey(Exception):
    pass
