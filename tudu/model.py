""" Database models """
import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

import tudu.exception as exception

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    list_id = Column(Integer, ForeignKey('list.id'))
    done = Column(Boolean, nullable=False, default=False)
    deadline = Column(DateTime)
    # priority setting options:
    # 0 - no notifications except for missed deadline
    # 1 - notify 1 day before deadline
    # 2 - notify a week before deadline, then 1 day before
    # 3 - notify everytime the app is opened
    priority = Column(Integer)
    # number of days of repeat interval
    repeat = Column(Integer, default=None)
    # notify is one three options:
    # (1)   a date of next actual notification
    # (2)   a day after deadline to serve as 'missed' notification
    #       if there are no more scheduled notifications
    # (3)   None if a 'missed' notification has been made
    notify = Column(DateTime, default=None)
    notes = Column(String(70))

    @validates('username')
    def validate_name(self, key, value):
        if value is None:
            raise ValueError('Task username not provided')
        elif len(value) > 45:
            raise ValueError('Task username too long')
        return value

    @validates('notes')
    def validate_name(self, key, value):
        """ Current word limit for a note is 70 characters """
        if value and len(value) > 70:
            raise ValueError('Notes too long')
        return value

    @validates('priority')
    def validate_priority(self, key, value):
        """ Check if deadline is in 0-3 range. Additional validation is done by subparser function """
        if value not in range(4):
            raise exception.PriorityError
        return value

    @validates('repeat')
    def validate_repeat(self, key, value):
        if value and value <= 0:
            raise ValueError('Repeat value has to be positive')
        return value

    # deadline validation is done by util.date_parser

    def __init__(self, name: str, deadline: datetime, priority: int, notes: str, repeat: int):
        self.name = name
        self.deadline = deadline
        self.priority = priority
        self.notes = notes
        self.repeat = repeat

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class List(Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    task_ids = relationship('Task')

    @validates('username')
    def validate_name(self, key, value):
        """ Check if username is not too long or reserved """
        banned_names = ['.']
        if value is None:
            raise ValueError
        elif len(value) > 45:
            raise ValueError('Name too long')
        elif value in banned_names:
            # . reserved for accessing current list in tui mode
            raise ValueError('This is not a valid username for a list')
        return value

    def __init__(self, name: str):
        self.name = name
