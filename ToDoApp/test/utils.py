from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from sqlalchemy import create_engine, text
from fastapi.testclient import TestClient
import pytest
from ..main import app
from ..models import Todos, Users 
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

'''With StaticPool:
Session 1 → Connection A
Session 2 → Connection A
Session 3 → Connection A

Everybody shares the same connection, so everybody sees the same test data.
The simplest way to think about it:
Production: many users → many connections 
Tests: one temporary test database → one shared connection'''

TestingSessionLocal = sessionmaker(autocommit= False, autoflush = False, bind = engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# mocks the user that is being sent for authentication
def override_get_current_user():
    return {'username': 'danaayyad', 'id': 1 , 'user_role' : 'admin'}


client = TestClient(app)


# fixture: something that we want tp create before the function is called
# Pytest does not understand FastAPI dependencies (Depends()), so we cannot inject db using Depends(override_get_db) inside pytest fixtures or tests.
@pytest.fixture
def test_todo():
    todo = Todos(
        title="learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1  # same id of the fake user
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo # continue the rest after the function finishes
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos")) # delete the todo
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username='danaayyad',
        email= 'test@gmail.com',
        first_name = 'Dana',
        last_name='Ayyad',
        hashed_password = bcrypt_context.hash("1234"),
        user_role= 'admin',
        phone_number = "(111)-111-111"
    )

    db= TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM USERS"))
        connection.commit()

