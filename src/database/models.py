from sqlalchemy import Column, Integer, String, Boolean, func, Table, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()

picture_m2m_tag = Table(
    "picture_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("picture_id", Integer, ForeignKey("pictures.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column("crated_at", DateTime, default=func.now())
    confirmed = Column(Boolean, default=False)
    role = Column(String(255), nullable=False, default="user")
    refresh_token = Column(String(255), nullable=True)
    is_banned = Column(Boolean, default=False)
    # pictures = relationship("Picture", back_populates="user")
    # comments = relationship("Comment", back_populates="user")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)


class Picture(Base):
    __tablename__ = "pictures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    description = Column(String(300), nullable=True)
    tags = relationship("Tag", secondary=picture_m2m_tag, backref="pictures")
    comments = relationship("Comment", backref="pictures")
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    qr_url = Column(String(255), nullable=True)


class Comment(Base):
    __tablename__ = "comments"
    # id = Column(Integer, primary_key=True, autoincrement=True)
    picture_id = Column(
        Integer, ForeignKey("pictures.id", ondelete="CASCADE"), primary_key=True
    )
    picture_comment_id = Column(Integer, primary_key=True)
    text = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    edited_at = Column(DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(
            "picture_id", "picture_comment_id", name="unique_pair_picture_comment"
        ),
    )
