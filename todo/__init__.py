from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.ddl import CreateTable
# from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError
import os
from todo.model import Task, List, Base
from sqlalchemy import create_engine


# db_path = f'{os.path.expanduser("~")}/.todo-todo-tasks.db'  db in home folder
# where the db will be created
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todo-tasks.db')
if not os.path.isfile(db_path):
    print(f'Creating a new database at {db_path}')
engine = create_engine(f'sqlite:///{db_path}')  # echo=True for debug

meta = MetaData()
meta.bind = engine
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
session = Session()

