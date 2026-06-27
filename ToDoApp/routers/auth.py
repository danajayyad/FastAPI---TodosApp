# scale the application for cleanness and maintainability (separate the logic)
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request  # APIRouter allow us to route from main.py to auth.py
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
''' Form() → “give me raw form fields”
OAuth2PasswordRequestForm → “give me a ready-made login form that follows security standards”
Normal Form	: General data input, You define fields yourself	
OAuth2PasswordRequestForm: Authentication login flow, Already predefined: username, password, scope (optional), grant_type (handled internally), 
follows the OAuth2 spec used in real authentication systems. That means it is compatible with: Swagger UI “Authorize” button, JWT authentication flows, token-based login systems
It expects:Content-Type: application/x-www-form-urlencoded'''

# app = FastAPI() # different fastapi application ?? separate port to run
# how to scale main and auth so they can run as one application on the same port while keeping it scalable and maintainable?

router = APIRouter(
    prefix='/auth', tags=['auth'] # prefix: This automatically adds /auth before every route in this router. ||| tags= This is mainly for Swagger docs (/docs). It groups endpoints visually.
) # it is a route instead of an entire application
#A router is a container/group for related routes.


# for jwt we need
SECRET_KEY = '9f3a1b2c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f708192a3b4c5d6e7f'
ALGORITHM = 'HS256'



# schemes means use the bcrypt algorithm, deprecated mean Automatically manage outdated hash schemes safely
'''Hashing is NOT encryption. You do NOT decrypt passwords later'''
# object (instance) of the CryptContext class
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
'''oauth2_bearer is mainly a tool/dependency that extracts the Bearer token from the request header.
OAuth2PasswordBearer(... ) creates the token extractor.

tokenUrl='token'
tells FastAPI:"If someone needs to obtain a token, they should go to /token" 
It does NOT mean: Extract token from /token

You are telling FastAPI:
Protected routes use Bearer tokens.
Users can obtain those tokens from auth/token.'''
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
# "Look inside Authorization header and extract Bearer token" , fastapi does: token = request.headers["Authorization"]


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password :str
    role: str
    phone_number : str

# no need for active because it is active by default on creation
# id is auto incremented by fastapi


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


'''JWT (JSON Web Token) is a secure way to transmit user-related information between client and server.
JWT is commonly used after login so the user does not need to authenticate again on every request.
After successful authentication (username/password), the server creates a JWT and sends it to the client.
The client stores the token and sends it with future requests, usually in:
Authorization: Bearer <token>
JWT parts: HEADER.PAYLOAD.SIGNATURE | header AND payload are usually only:Base64 encoded NOT encrypted. Base64 is just a representation format. It is reversible by anyone. signature = hash(header + payload + secret)
The hashing/signing process is one-way.
That means: you can CREATE the signature from the data + secret but you cannot reverse the signature to discover the secret key
Important Security Facts
JWT payload is usually ENCODED, not encrypted.
Anyone with the token can usually decode and read the payload.
Therefore:Do NOT store passwords or sensitive secrets inside JWTs. JWT enables stateless APIs.
Meaning:the server does NOT need to store session data for logged-in users. the token itself contains the user identity. Each request includes everything needed to identify the user.
Authentication
(login with username/password)
↓
Server creates JWT
↓
Authorization
(user accesses protected routes using token)'''


def create_access_token(username: str, user_id: int, role: str,  expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role} #Creates the JWT payload. Example result: { 'sub': 'Dana',   'id': 15 }
    expires = datetime.now(timezone.utc) + expires_delta # Using UTC avoids timezone problems between servers and users.. when the token will expire, now + expiration e.g ( 10:00 + 30 min -> 10:30 expires)
    encode.update({'exp': expires}) # add key value to the encode payload. The header is created automatically by the JWT library. :{  "alg": "HS256", "typ": "JWT"}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Authenticate/validate the TOKEN (later requests):  the server no longer checks password again. Instead it checks: "Is this token valid and trustworthy?"
# FastAPI calls dependency → FastAPI writes await when calling it
async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]): #token is a string, and FastAPI should get it using oauth2_bearer
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # If the payload changes, then the correct signature must also change,because the signature depends on the payload + secret key. But the attacker does not know the secret key, so they cannot generate the correct new signature for the modified payload. Therefore, when the server recalculates the expected signature using: the received header the received payload the server secret key the result will NOT match the signature sent inside the token. So the server concludes: "This token was modified or forged." and rejects it.The server cannot always know WHY the mismatch happened. A mismatch could mean: payload tampering, fake token, wrong secret, corrupted token
        '''What jwt.decode()
        Splits JWT gets separated into:  header  payload signature Then Reads header recomputes the expected signature using: header payload SECRET_KEY Then compares it with the token’s signature. If signatures do NOT match Then decoding fails with an exception
        Checks expiration If payload contains: { "exp": ...}
        PyJWT checks:
        is token expired?
        If expired: exception raised
        Returns payload  If everything is valid: payload becomes a normal Python dictionary. Example: {
            'sub': 'Dana',
            'id': 15,
            'exp': 1719999999
        }'''
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None : # The signature guarantees: "No one modified the payload after signing." (checks cryptographic validity.) |||| But the server still must check: "Does this payload contain the information I require?" (checks application requirements.)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


'''A route (one endpoint) defines:defines URL path, HTTP method, function to execute while an endpoint is the actual accessible API location/functionality exposed to the client.'''


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # create_user_model = Users(**create_user_request.dict()) we cant now because we are passing password not hashed password
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
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

