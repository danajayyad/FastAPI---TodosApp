'''So what is a database?
Well, a database is an organized collection of structured information, of data which is stored in
a computer system.
The data can be easily accessed.
The data can be modified.
The data can be controlled and organized.
SQL is the standard language for dealing with relational databases.
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#create a location of the database in our fastapi app, inside the directory that im currently in
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# SQLALCHEMY_DATABASE_URL= 'postgresql://postgres:1234@localhost/TodoApplicationDatabase'
# db type, username, password, host(server), database name
# port is by default:localhost:5432

# SQLALCHEMY_DATABASE_URL='mysql+pymysql://root:root@127.0.0.1:3306/TodoApplicationDatabase'


# db engine used to open a connection and use the db
# engine is created once globally when the app starts.
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread' : False}) # “Do not enforce the one-thread-only rule. If Thread 1 created or started using a SQLite connection, SQLite normally wants ONLY Thread 1 to use it. But in FastAPI, another request may be handled by Thread 2, and Thread 2 may also need database access.
# Without: check_same_thread=False, SQLite may reject Thread 2 using that connection.


engine = create_engine(SQLALCHEMY_DATABASE_URL)




SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # commit saves changes permenantly to the db, false means SQLAlchemy does NOT automatically save changes. flush() is useful when you need the database to process the changes before the final commit, False means dont flush unless we say (flush may be used to get data for another query before commititng everyhting). bind tells sessoion which db to use
# sessionmaker is a SQLAlchemy utility that creates a session factory. A factory means: something that creates objects for you.
#  SessionLocal is not an actual session, it is a blueprint or a machine to create sessions
#  Without a factory, you would need to manually create and configure every session:
#  db = Session(
#     bind=engine,
#     autocommit=False,
#     autoflush=False)

Base = declarative_base() # fucntion builds and returns the parent class base that will be use when creating tables


