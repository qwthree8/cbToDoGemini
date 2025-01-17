from tokenize import Token

from fastapi import FastAPI, Depends, Path, Query, HTTPException, APIRouter
from jose.constants import ALGORITHMS
from starlette import status
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session, sessionmaker
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime,timezone

router = APIRouter(
    prefix="/Auth",
    tags = ["Authentication"]
)

SECRET_KEY_ = "3DXpcxG92ğİ^'3+5dnv.%?*sdv<xLs38fgJG688er7TDFnd80DI88hdasnXMCLcs"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/Auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db #birden fazla veri döndürmek için
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

def create_acces_token(username:str , user_id:int ,role:str , expires_delta: timedelta):
    payload = {"sub": username , "id": user_id , "role": role}
    expires = datetime.now(timezone.utc) + expires_delta #datetime.now(timezone.utc) = çalıştığı andaki zamani verir ( geçerlilik süresi)
    payload.update({"exp":expires}) #sürenin ne zaman geçerli olmayacağını belirttik
    return jwt.encode(payload, SECRET_KEY_, algorithm=ALGORITHM)


class CreateUserRequest(BaseModel):
    username : str
    email : str
    first_name : str
    last_name : str
    password : str
    role : str

class Token(BaseModel):
    access_token: str
    token_type:  str

def authenticate_user(username: str,password: str , db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password): #user ile password uyumu kontrolü. ikiside aynı kişiye mi ait
        return False
    return user


async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):#token encode ve kontrol
    try:
        payload = jwt.decode(token, SECRET_KEY_,algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id  = payload.get("id")
        user_role = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="username or ID is invalid")
        return {"username": username ,"id":user_id ,"role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is invalid")


@router.post("/Register",status_code=status.HTTP_201_CREATED)
async def create_user (db: db_dependency, create_user_request: CreateUserRequest):
    user = User(
        username = create_user_request.username,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        is_active = True,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )
    db.add(user)
    db.commit()

@router.delete("/delete/{selected_id}",status_code=status.HTTP_200_OK)
async def delete_user (db: db_dependency ,  selected_id: int = Path(gt=0)):
    delete = db.query(User).filter(selected_id == User.id).first()
    if delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(delete)
    db.commit()

@router.post("/token", response_model = Token)
async def login_for_access_token(db: db_dependency,
                                form_data: Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Username not found")
    token = create_acces_token(user.username, user.id,  user.role, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}
