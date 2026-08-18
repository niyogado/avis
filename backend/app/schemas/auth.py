from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class userLogin(BaseModel):
    email:EmailStr
    password:str
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    username: str
    phone: str

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    first_name: str
    last_name: str
    username: str
    phone: str

    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

