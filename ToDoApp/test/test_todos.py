from starlette import status
from ..routers.todos import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db  # Whenever FastAPI needs get_db, use override_get_db instead.
app.dependency_overrides[get_current_user] = override_get_current_user


# Many components work together: this is an integration test.
def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id':1, 'title':'learn to code',
                                'description':'Need to learn everyday',
                                'priority':'5',
                                'complete':False,
                                'owner_id':1  }] 


# if the todo is found
def test_read_one_authenticated(test_todo):
    response = client.get('/todos/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id':1, 'title':'learn to code',
                                'description':'Need to learn everyday',
                                'priority':'5',
                                'complete':False,
                                'owner_id':1  } 


# if the todo is not found
def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todos/todo/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'Todo not found.'}



def test_create_todo(test_todo):
    request_data= {'title': 'New todo',
                     'description': 'Need todo description',
                     'priority': '5',
                     'complete': False}
    response = client.post('/todos/todo/' , json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(test_todo):
    request_data = {'title': 'Updated TItle of New todo ',
                     'description': 'Need todo description updated',
                     'priority': '5',
                     'complete': False}
    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')


def test_update_todo_not_found(test_todo):
    request_data = {'title': 'Updated TItle of New todo ',
                     'description': 'Need todo description updated',
                     'priority': '5',
                     'complete': False}
    response = client.put('/todos/todo/7565', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail' : 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete('/todos/todo/32323')
    assert response.status_code == 404
    assert response.json() == {'detail' : 'Todo not found'}

