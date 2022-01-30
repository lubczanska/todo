import sqlalchemy
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from sqlalchemy import func

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    list = Column(Integer, ForeignKey('list.id'))  # TODO refactor to list_id
    done = Column(Boolean, nullable=False, default=False)
    deadline = Column(DateTime)
    # priority setting options:
    # 0 - no notifications except for missed deadline
    # 1 - notify 1 day before deadline
    # 2 - notify a week before deadline, then 1 day before
    # 3 - notify everytime the app is opened
    priority = Column(Integer)
    # number of days of repeat interval TODO: change to int
    repeat = Column(String, default=None)
    # notify is one three options:
    # (1)   a date of next actual notification
    # (2)   a day after deadline to serve as 'missed' notification
    #       if there are no more scheduled notifications
    # (3)   None if a 'missed' notification has been made
    notify = Column(DateTime, default=None)
    notes = Column(String)

    def __init__(self, name, deadline, priority, notes, repeat):
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
    name = Column(String)
    tasks = relationship('Task')  # TODO refactor to task_ids

    def __init__(self, name):
        self.name = name
