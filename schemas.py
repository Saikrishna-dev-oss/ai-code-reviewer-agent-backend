from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class LogCreate(BaseModel):
    level: str
    logger_name: str
    message: str
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None

class LogResponse(LogCreate):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None
    error_type: Optional[str] = None
