from typing import List, Dict

from sqlalchemy.orm import Session

from src.schemas import CommentBase, PictureBase
from src.database.models import Comment, Picture, Tag, picture_m2m_tag
from src.schemas import PictureResponse, PictureResponseDetails

from fastapi import Depends
from src.database.db import get_db


from fastapi import Depends, HTTPException, status
from src.services.exceptions import (TAG_IS_ALREADY_ASSIGNED_TO_PICTURE,
                                          PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED,
                                          TAG_IS_ALREADY_ASSIGNED_TO_PICTURE_AND_PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED,
                                          )


async def add_picture(
    url: str, public_id: str, description: str, db: Session
) -> Picture:
    new_picture = Picture(url=url, public_id=public_id, description=description)
    db.add(new_picture)
    db.commit()
    db.refresh(new_picture)
    return new_picture

async def add_tag(picture_id: int, tag_id: int, db: Session):
    picture = db.query(Picture).filter( Picture.id == picture_id ).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if (len(picture.tags)>=5) and (tag in picture.tags):
        return TAG_IS_ALREADY_ASSIGNED_TO_PICTURE_AND_PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED

    if len(picture.tags)>=5:
        return PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED

    if tag in picture.tags:
        return TAG_IS_ALREADY_ASSIGNED_TO_PICTURE

    picture.tags.append(tag)
    db.commit()
    return 0
async def delete_tag(tag_id: int, picture_id: int, db: Session):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if tag not in picture.tags:
        return -4
    picture.tags.delete(tag)
    db.commit()
    return 0

async def get_pictures(db: Session) -> List[Picture]:
    pictures = db.query(Picture).filter(Picture.is_deleted == False).all()
    return pictures


async def get_picture(picture_id: int, db: Session) -> Picture:
    picture = (
        db.query(Picture)
        .filter(Picture.id == picture_id)
        .filter(Picture.is_deleted == False)
        .first()
    )
    return picture


# async def get_picture_details(picture_id: int, db: Session):
#     picture = db.query(Picture).filter(Picture.id == picture_id).first()
#     return picture


async def edit_picture_description(picture_id: int, db: Session, new_description: str) -> Picture:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture != None:
        picture.description = new_description
        db.commit()
        db.refresh(picture)
    return picture


async def delete_picture(picture_id: int, db: Session) -> Picture:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture != None:
        picture.is_deleted = True
        db.commit()
        db.refresh(picture)
    return picture


# async def get_description(picture_id: int, db: Session):
#     description = (
#         db.query(Picture).filter(Picture.id == picture_id).value(Picture.description)
#     )
#     print(description)
#     return description
