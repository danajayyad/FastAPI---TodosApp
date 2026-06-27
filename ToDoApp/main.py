from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine # . is for the exact directory this is in
from .routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()


# Accessing the Base object from the models module. models.Base (i want the base that have the tables registered in it )
# "SQLAlchemy only knows about tables after the Python modules containing the model classes have been imported and executed." this is why we need to import the folder
Base.metadata.create_all(bind=engine) #Models defined → Base collects them → metadata stores them → create_all() creates tables in DB




# A mounted path is simply the URL prefix that FastAPI watches for. means:Attach something to a URL path.
# Any URL that starts with /static should be handled by the static-file system.
# StaticFiles(...) This creates a special object whose job is "Find files on disk and send them to the browser."
# Whenever a request starts with /static, send it to the StaticFiles handler.
# name="static" This gives the mounted route a name.
# So when a request arrives:
# /static/style.css FastAPI matches: /static and removes that part. What's left is:  style.css  Then it looks for: TodoApp/static/style.css
app.mount("/static", StaticFiles(directory="ToDoApp/static"), name="static")
# URL                     File on disk
# -------------------------------------------------
# /static/css/base.css -> ToDoApp/static/css/base.css
# /static/logo.png     -> ToDoApp/static/logo.png


# request is not something you create yourself.
# FastAPI automatically creates it from the incoming browser request.

# The browser sends an HTTP request that looks roughly like:
# GET / HTTP/1.1 Host: 127.0.0.1:8000 User-Agent: Chrome

# FastAPI receives that request and creates a Request object containing information about the request (URL, headers, cookies, etc.).

# FastAPI then calls your route function and passes that Request object into the 'request' parameter.g

# if  name="static"     <-- internal name used by url_for()
#"/test" <-- actual URL seen by browser then {{ url_for('static', path='style.css') }}  becomes:/test/style.css


# 1-  browser requests the page
@app.get("/")
def test(request:Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


# health check
@app.get('/healthy')
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router) # router is the name of the APIrouter in auth.py
# Take all the routes inside auth.router and add them to the main FastAPI application.
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)