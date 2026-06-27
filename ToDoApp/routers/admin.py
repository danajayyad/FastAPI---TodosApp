from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from ..models import Todos # ..  means 2 files out
from ..database import SessionLocal
from .auth import get_current_user #. = current package (routers folder)

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal() # create a new database session (connection handler)
    try:
        yield db # pass the session to the api
    finally: # executed after the response is delivered (this makes the fastapi faster because we can fetch the db, send to the client and then close the connection)
        db.close()


db_dependency = Annotated[Session, Depends(get_db)] # dependency is stored (Not an actual session)
user_dependency = Annotated[dict, Depends(get_current_user)]

'''
Anyone can still send requests to: /admin/todo
A normal user could manually call:
GET /admin/todo Authorization: Bearer normal_user_token
If you DID NOT check role: user.get('user_role') != 'admin'
then the normal user would successfully access: all todos,  admin data
Huge security problem.
So this check is the REAL protection
if user is None or user.get('user_role') != 'admin':
'''


@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all() # admin can see all todos for all users


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

