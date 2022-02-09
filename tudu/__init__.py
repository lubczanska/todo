""" A simple to-do list manager

Provides a cli or tui tool for managing to-do lists including setting deadlines, scheduling notifications,
repeating tasks and sticky note style task displaying
"""

import os

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tudu.model import Task, List, Base

# where the db will be created
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tudu-tasks.db')
if not os.path.isfile(db_path):
    print(f'Creating a new database at {db_path}')
engine = create_engine(f'sqlite:///{db_path}')

meta = MetaData()
meta.bind = engine
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
session = Session()
