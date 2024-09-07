from datetime import datetime
from typing import Optional, List
from sqlalchemy import Table, Column, create_engine, ForeignKey, Integer
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

DATABASE_URL = 'sqlite:///test.db'


class NotFoundError(Exception):
    pass

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()