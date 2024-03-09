from enum import Enum

from pydantic import BaseModel, Field, EmailStr
from typing import List
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


class Id(BaseModel):

    id: int

    class Config:
        from_attributes = True


class CommentDates(BaseModel):

    created_at: datetime
    edited_at: datetime

    class Config:
        from_attributes = True


class CommentResponse(CommentBase, CommentDates):

    picture_id: int
    picture_comment_id: int

    pass


class Comment2Display(CommentBase, CommentDates):

    pass


class TagResponse(BaseModel):

    name: str

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=16)
    email: str
    password: str = Field(min_length=2, max_length=16)
    # is_banned: bool = False


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class UserUpdateModel(BaseModel):
    username: str = Field(min_length=4, max_length=15)


class UserRoleEnum(str, Enum):
    ADMIN = "administrator"
    MOD = "moderator"
    USER = "user"


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
        from_attributes = True


class QRCodeModel(BaseModel):
    id: int
    url: str
    transformed_picture_url: int

    class Config:
        from_attributes = True


class QRCodeRequest(BaseModel):
    transformed_photo_url: str


class PictureBase(BaseModel):
    public_id: str | None
    url: str


class PictureResponse(Id):

    public_id: str
    url: str
    description: str | None


class PictureResponseDetails(PictureResponse):

    tags: list[TagResponse]
    comments: list[Comment2Display]

    #     __tablename__ = "pictures"
    # id = Column(Integer, primary_key=True, autoincrement=True)
    # public_id = Column(String(255), nullable=True)
    # url = Column(String(255), nullable=True)
    # description = Column(String(300), nullable=True)
    # tags = relationship("Tag", secondary=picture_m2m_tag, backref="pictures")
    # comments = relationship("Comment", backref="pictures")
    # is_deleted = Column(Boolean, default=False)
