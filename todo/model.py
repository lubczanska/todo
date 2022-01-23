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
    list = Column(Integer, ForeignKey('list.id'))
    done = Column(Boolean, nullable=False, default=False)
    deadline = Column(DateTime)
    priority = Column(Integer)
    notes = Column(String)

    def __init__(self, name, deadline, priority, notes):
        self.name = name
        self.deadline = deadline
        self.priority = priority
        self.notes = notes

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class List(Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tasks = relationship('Task')

    def __init__(self, name):
        self.name = name
