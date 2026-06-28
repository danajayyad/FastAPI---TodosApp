from fastapi import APIRouter, Depends, HTTPException, Request, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user #. = current package (routers folder)
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='ToDoApp/templates')

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal() # create a new database session (connection handler)
    try:
        yield db # pass the session to the api
    finally: # executed after the response is delivered (this makes the fastapi faster because we can fetch the db, send to the client and then close the connection)
        db.close()


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)] # dependency is stored (Not an actual session)
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=4)


@router.get('/change-password')
def change_password_page(request:Request):
    return templates.TemplateResponse(
        name="change-password.html",
        request=request,

    )



@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    return db.query(Users).filter(Users.username == user.get('username')).first()


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.username == user.get('username')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password) # bcrypt_context.verify( entered_password,   stored_hash)
    db.add(user_model) # So SQLAlchemy already knows: this object exists in DB , its primary key , it is being tracked by the session
    db.commit()


# better be a request body and a pydantic checks on it
@router.put('/phonenumber/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail= 'Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()

