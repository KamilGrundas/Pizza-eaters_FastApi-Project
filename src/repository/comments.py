from typing import List

from sqlalchemy.orm import Session

from src.schemas import CommentBase
from src.database.models import Comment


async def create_new_comment(
    body: CommentBase, db: Session, picture_id: int
) -> Comment:
    # docelowo będzie tu jeszcze User
    comment = Comment(picture_id=picture_id, text=body.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment(db: Session, comment_id: int) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    comment.is_deleted = True
    db.commit()
    return comment


async def edit_comment(body: CommentBase, db: Session, comment_id: int) -> Comment:
    comment = await get_comment(db, comment_id)
    if comment:
        comment.text = body.text
    db.commit()
    return comment


async def get_comments(db: Session, picture_id: int) -> List[Comment]:

    comments = (
        db.query(Comment)
        .filter(Comment.picture_id == picture_id)
        .filter(Comment.is_deleted == False)
        .all()
    )
    return comments


async def get_comment(db: Session, comment_id: int) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    return comment
