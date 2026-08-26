from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request 
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from config import settings

router = APIRouter(
    prefix='/auth', tags=['auth']
)


# for jwt we need
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password :str
    role: str
    phone_number : str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="ToDoApp/templates")


### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(name="register.html", request=request)


### Endpoints ###
# Authenticate the USER (during login): "Is this really Dana?" Server checks: username and password
def authenticate_user(username: str, password: str , db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password): # this will automatically hash the password and compare the result with the hashed password and will return true or false
        return False
    return user




def create_access_token(username: str, user_id: int, role: str,  expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role} 
    expires = datetime.now(timezone.utc) + expires_delta 
    encode.update({'exp': expires}) 
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Authenticate/validate the TOKEN (later requests):  the server no longer checks password again. Instead it checks: "Is this token valid and trustworthy?"
# FastAPI calls dependency → FastAPI writes await when calling it
async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]): #token is a string, and FastAPI should get it using oauth2_bearer
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None : # The signature guarantees: "No one modified the payload after signing." (checks cryptographic validity.) |||| But the server still must check: "Does this payload contain the information I require?" (checks application requirements.)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()


# called on login
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': token, 'token_type': 'bearer'}

