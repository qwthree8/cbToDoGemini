from starlette import status
from pydantic import BaseModel, Field
from fastapi import FastAPI,Depends,Path,Query, HTTPException
from sqlalchemy.orm import Session
from models import Base, Todo
from database import engine, SessionLocal
from typing import Annotated


app = FastAPI()

Base.metadata.create_all(bind=engine)

class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3 , max_length= 3000)
    priority : int  = Field(gt=0, lt = 6)
    complete : bool


def get_db():
    db = SessionLocal()
    try:
        yield db #birden fazla veri döndürmek için
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/read_all")
async def read_all(db: db_dependency):
    return db.query(Todo).all()


@app.get("/read_one/{todo_id}", status_code =status.HTTP_200_OK)
async def read_by_id(db: db_dependency, todo_id: int = Path(gt = 0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first() #first ilk gelen elemanı döndürecek
    if todo is not None:
        return todo
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "todo not found" )


@app.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db:db_dependency, todo_request: TodoRequest):
    todo = Todo(**todo_request.dict())
    db.add(todo)
    db.commit()#add dedikten sonra commit demez isek çalışmaz. işlemin yapılacağı anlamına gelir

