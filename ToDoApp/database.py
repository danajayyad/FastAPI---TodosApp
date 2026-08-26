from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",  # prodduction, cloud service
    "sqlite:///./todosapp.db" # locally
)

# Handle older postgres:// URLs if necessary
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1,
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL)




SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base() # fucntion builds and returns the parent class base that will be use when creating tables


