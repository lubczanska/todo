from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.ddl import CreateTable
# from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError

from todo.model import Task, List, Base
from sqlalchemy import create_engine

engine = create_engine('sqlite:///tasks.db')  # echo=True for debug

meta = MetaData()
meta.bind = engine
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
session = Session()

