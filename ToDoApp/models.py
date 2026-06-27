from .database import Base # importing the base created in the database.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


# ORM models are Python classes that represent tables.(blueprints for the actual tables)
# inherits from that Base SQLAlchemy registers the Todos table inside Base.metadata


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


class Todos(Base):
    __tablename__ = 'todos' # name od the table in the database

    id = Column(Integer, primary_key=True, index=True) # index is to increase performance. Because the id is unique , sqlalchemy will automatically give it a value and will increment
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id")) # reference on users table id column


