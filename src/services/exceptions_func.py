from typing import List

from sqlalchemy.orm import Session

from src.database.models import Comment, Picture


from fastapi import HTTPException, status


def no_picture_exception(picture_id: int, db: Session):
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if bool(picture) == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found"
        )


def no_comment_exception(comment_id: int, db: Session):

    exc = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if bool(comment) == False:
        raise exc
    if comment.is_deleted:
        raise exc
