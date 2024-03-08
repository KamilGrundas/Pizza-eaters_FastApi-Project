from typing import List

from sqlalchemy.orm import Session

from src.database.models import Picture



async def add_picture(
    url: str, public_id: str, description: str, db: Session
) -> Picture:
    new_picture = Picture(url=url, public_id=public_id, description=description)
    db.add(new_picture)
    db.commit()
    db.refresh(new_picture)
    return new_picture


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
