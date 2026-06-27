from fastapi.testclient import TestClient
from .. main import app # the main.py of the entire project
from fastapi import status


# TestClient as a fake browser/Postman that talks directly to your FastAPI application. No Uvicorn, No real network request
client = TestClient(app)


def test_return_health_check():
    response = client.get('/healthy')  #Just like typing: http://localhost:8000/healthy in a browser.
    assert response.status_code == status.HTTP_200_OK # because route doesnt define status code, FastAPI uses its default: 200 OK
    assert response.json() == {'status': 'Healthy'}
