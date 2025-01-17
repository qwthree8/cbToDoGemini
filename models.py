from numpy.ma.extras import unique

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, column, ForeignKey


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index = True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean,default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))#Auth kısmındaki id ile eşleştirdik.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True , index= True)
    email = Column(String, unique = True)#burda bir mail adresinden 2 kere database de olamaz diye kural ekledik
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)
