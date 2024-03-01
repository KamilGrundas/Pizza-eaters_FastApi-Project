from pydantic import BaseModel, Field
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
