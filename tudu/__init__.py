""" Initialize database and session """
import os

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tudu.model import Task, List, Base

# where the db will be created
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tudu-tasks.db')
if not os.path.isfile(db_path):
    print(f'Creating a new database at {db_path}')
engine = create_engine(f'sqlite:///{db_path}')  # echo=True for debug

meta = MetaData()
meta.bind = engine
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
session = Session()


