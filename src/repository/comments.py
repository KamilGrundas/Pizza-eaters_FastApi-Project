from typing import List

from sqlalchemy.orm import Session

from src.schemas import CommentBase
from src.database.models import Comment, User


async def create_new_comment(
    body: CommentBase, db: Session, picture_id: int, author: User
) -> Comment:
    # docelowo będzie tu jeszcze User
    picture_comments_num = (
        db.query(Comment).filter(Comment.picture_id == picture_id).count()
    )

    print(picture_comments_num)

    comment = Comment(
        picture_id=picture_id,
        picture_comment_id=picture_comments_num + 1,
        text=body.text,
        user_id=author.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment(
    db: Session, picture_id: int, picture_comment_id: int
) -> Comment:
    comment = (
        db.query(Comment)
        .filter(
            Comment.picture_id == picture_id,
            Comment.picture_comment_id == picture_comment_id,
        )
        .first()
    )
    comment.is_deleted = True
    db.commit()
    return comment


async def edit_comment(
    body: CommentBase, db: Session, picture_id: int, picture_comment_id: int
) -> Comment:
    comment = await get_comment(db, picture_id, picture_comment_id)
    if comment:
        comment.text = body.text
    db.commit()
    return comment


async def get_comments(db: Session, picture_id: int) -> List[Comment]:

    comments = (
        db.query(Comment)
        .filter(
            Comment.picture_id == picture_id,
        )
        .filter(Comment.is_deleted == False)
        .all()
    )
    return comments


async def get_comment(db: Session, picture_id: int, picture_comment_id: int) -> Comment:
    comment = (
        db.query(Comment)
        .filter(
            Comment.picture_id == picture_id,
            Comment.picture_comment_id == picture_comment_id,
        )
        .first()
    )
    return comment
