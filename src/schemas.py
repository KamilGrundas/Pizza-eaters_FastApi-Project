from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class CommentBase(BaseModel):
    # class Comment(Base):
    #     __tablename__ = "comments"
    #     id = Column(Integer, primary_key=True, autoincrement=True)
    #     text = Column(String(200), nullable=False)
    #     picture_id = Column(Integer, ForeignKey("pictures.id", ondelete="CASCADE"))
    #     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    #     created_at = Column(DateTime, default=func.now())
    #     edited_at = Column(DateTime, default=func.now())

    text: str = Field(max_length=200)


class CommentResponse(CommentBase):

    id: int
    created_at: datetime
    edited_at: datetime

    class Config:
        from_attributes = True



class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=8, max_length=16)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr

class TagModel(BaseModel):
    name: str = Field(max_length=25)

class TagResponse(TagModel):
    id: int

    class Config:
        orm_mode = True