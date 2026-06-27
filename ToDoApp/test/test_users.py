from starlette import status

from .utils import *
from ..routers.users import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json()['username'] =='danaayyad'
    assert response.json()['email'] == 'test@gmail.com'
    assert response.json()['first_name'] == 'Dana'
    assert response.json()['last_name'] == 'Ayyad'
    assert response.json()['user_role'] == 'admin'
    assert response.json()['phone_number'] == "(111)-111-111"





def test_change_password(test_user):
    user_verification_test = {'password' : '1234', 'new_password' : '4321'}
    response = client.put('/user/password', json=user_verification_test)
    assert response.status_code == 204

    db = TestingSessionLocal()
    user_model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify( user_verification_test.get('new_password'), user_model.hashed_password)


def test_change_password_invalid(test_user):
        user_verification_test = {'password': 'wrongPassword', 'new_password': '4321'}
        response = client.put('/user/password', json=user_verification_test)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail' : 'Error on password change'}


def test_change_phone_number_success(test_user):
    response= client.put('/user/phonenumber/33333333333')
    assert response.status_code == 204
