from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine # . is for the exact directory this is in
from .routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()
Base.metadata.create_all(bind=engine) 

app.mount("/static", StaticFiles(directory="ToDoApp/static"), name="static")

# 1-  browser requests the page
@app.get("/")
def test(request:Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


# health check
@app.get('/healthy')
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)