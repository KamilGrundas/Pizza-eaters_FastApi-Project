from sqlalchemy import Column, Integer, String, Boolean, func, Table
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
    # role = Column()
    admin = Column(Boolean, default=False)
    mod = Column(Boolean, default=False)
    standard_user = Column(Boolean, default=False)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
    
    

class Picture(Base):
    __tablename__ = "pictures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tags = relationship("Tag", secondary=picture_m2m_tag, backref="pictures")
    # wstawiłam tyle tylko, żeby mi lokalnie błędu nie wywalało - Olka


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    picture_id = Column(Integer, ForeignKey("pictures.id", ondelete="CASCADE"))
    text = Column(String(200), nullable=False)
    # user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE")) - to na potem
    created_at = Column(DateTime, default=func.now())
    edited_at = Column(DateTime, default=func.now())
    is_deleted = Column(
        Boolean, default=False
    )  # to jest soft delete ;) komentarz po usunięciu będzie w bazie danych ale nie będzie wyświetlany
    