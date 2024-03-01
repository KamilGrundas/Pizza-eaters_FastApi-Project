from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=8, max_length=16)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    role: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    STANDARD_USER = "standard_user"


class UserRole(BaseModel):
    role: UserRoleEnum


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
