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
    list = Column(Integer, ForeignKey('List.id'))
    done = Column(Boolean, nullable=False, default=False)
    deadline = Column(DateTime)
    priority = Column(Integer)
    notes = Column(String)

class List(Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tasks = relationship('Task', foreign_keys='Task.list')