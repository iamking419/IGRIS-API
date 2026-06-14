from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PairRequest(BaseModel):
    code: int


class UserLogin(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None
    user_id: int | None = None




class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None


class ChatSessionCreate(BaseModel):
    title: str = "New Chat"


class ChatSessionOut(BaseModel):
    id: int
    title: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True