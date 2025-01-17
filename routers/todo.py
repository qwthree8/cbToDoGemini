from starlette import status
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, Path, Query, HTTPException, APIRouter
from sqlalchemy.orm import Session
from models import Base, Todo
from database import engine, SessionLocal
from typing import Annotated


router = APIRouter(
    prefix="/todo",
    tags = ["Todo"]
)


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3 , max_length= 1000)
    priority : int  = Field(gt=0, lt = 6)
    complete : bool


def get_db():
    db = SessionLocal()
    try:
        yield db #birden fazla veri döndürmek için
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/get_all")
async def get_all(db: db_dependency):
    return db.query(Todo).all()


@router.get("/read_one/{todo_id}", status_code =status.HTTP_200_OK)
async def read_by_id(db: db_dependency, todo_id: int = Path(gt = 0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()  #first ilk gelen elemanı döndürecek
    if todo is not None:
        return todo
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "todo not found" )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create(db:db_dependency, todo_request: TodoRequest):
    todo = Todo(**todo_request.model_dump())
    db.add(todo)
    db.commit()#add dedikten sonra commit demez isek çalışmaz. işlemin yapılacağı anlamına gelir

@router.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update(db:db_dependency,
                   todo_request: TodoRequest,
                   todo_id: int = Path(gt=0)):

    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete
    db.add(todo)
    db.commit()
@router.delete("/delete/{todo_id}", status_code=status.HTTP_200_OK)
async def delete(db:db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(todo_id == Todo.id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    '''db.query(Todo).filter(Todo.id == todo_id).delete() =  silme yöntemlerinden birisi. garanticiler bunu kullanabiliyor :)'''
    db.delete(todo)
    db.commit()