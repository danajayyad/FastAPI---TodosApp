from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user #. = current package (routers folder)
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='ToDoApp/templates')

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

'''ORM models are blueprints for tables
Base collects all those blueprints
metadata is the registry holding table definitions
create_all builds real tables from metadata'''




# anything that includes the yield and above it will be executed before sending a response
#Depends() in FastAPI is specifically used to declare dependencies that are necessary for your application or function to operate correctly. This mechanism allows FastAPI to automatically inject these dependencies at runtime, ensuring your code is modular and maintainable
def get_db():
    db = SessionLocal() # create a new database session (connection handler)
    try:
        yield db # pass the session to the api
    finally: # executed after the response is delivered (this makes the fastapi faster because we can fetch the db, send to the client and then close the connection)
        db.close()


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3 , max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


'to reduce redendancy'
db_dependency = Annotated[Session, Depends(get_db)] # dependency is stored (Not an actual session)
'''db should be:
- created using get_db()
- injected into the endpoint
- treated as a Session'''

user_dependency = Annotated[dict, Depends(get_current_user)]


def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND) # The browser receives something like: HTTP/1.1 302 Found Location: /auth/login-page When it sees the Location header, it automatically makes another request: GET /auth/login-page So the user ends up on the login page.
    redirect_response.delete_cookie(key="access_token") # modify response before sending it, to remove cookie to avoid keeping expired
    return redirect_response


### Pages ###
@router.get('/todo-page')
async def render_todo_page(request: Request, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token')) # we are gettiing the user based on the access token saved in the cookies not based on the bearer in the header
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse(
            name="todo.html",
            request=request,
            context={
                "user": user,
                "todos": todos
            }
        )
    except:
        return redirect_to_login()


@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse(
            name="add-todo.html",
            request=request,
            context={
                "user": user
            }
        )
    except:
        return redirect_to_login()


@router.get('/edit-todo-page/{todo_id}')
async def edit_todo(request: Request, todo_id:int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse(
            name="edit-todo.html",
            request=request,
            context={
                "user": user,
                "todo" :todo
            })

    except:
        return redirect_to_login()




### Endpoints ###
@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency , db: Annotated[Session, Depends(get_db)]): # Dependecy Injection, get_db is being passed as a function, then fastapi calls it and retrun its value. db is a Session, and FastAPI should inject it using get_db." name: Annotated[type, extra_information], Depends means: before running the endpoint, excecute get_db and the type will be Session and will be names db
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all() # after this, fastapi resumes get_db (the finally block)


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK) #explicit status response. return this status always unless failed
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)): #db should be a SQLAlchemy Session provided using get_db(). Path() is built is validation for the path [arameter (returnd 422 is not match the required rules) and it is treated as a parameter with a default, it should be at the last of the params list
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = (db.query(Todos).filter(Todos.id == todo_id).filter( Todos.owner_id == user.get('id')).first()) # one Todos object (one database row)
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')


'''“db.query(Todos) -> Start a query on the Todos table.”
Todos is the ORM model representing the database table.
Equivalent SQL idea: SELECT * FROM todos.
.filter(Todos.id == todo_id) -> Equivalent SQL: WHERE id = 3'''


# "user is a dictionary that FastAPI will provide by running get_current_user() first", so instead of typing this in user: dict = Depends(get_current_user), we do user: user_dependency and behind the scene this happens: user = get_current_user(token)
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Todos(**todo_request.dict(), owner_id = user.get('id'))
    db.add(todo_model) # making db ready to add
    db.commit() # flushing it all and do transaction to db


@router.put("/todo/{todo_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None: # the todo we want to update is not found
        raise HTTPException(status_code=404, detail='Todo not found.')

    # update the row we retrieved
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    # db.delete(todo_model)
    db.commit()
