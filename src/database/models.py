from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# photo_m2m_tag = Table(
#     "note_m2m_tag",
#     Base.metadata,
#     Column("id", Integer, primary_key=True),
#     Column("photo_id", Integer, ForeignKey("photo.id", ondelete="CASCADE")),
#     Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
# )

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

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)

#class Photos(Bsed) to be created