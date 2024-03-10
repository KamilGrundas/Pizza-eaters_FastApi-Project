from typing import List

from sqlalchemy.orm import Session

from src.schemas import CommentBase
from src.database.models import Comment, User
from src.services.exceptions import check_if_picture_exists


async def add_comment(
    body: CommentBase, db: Session, picture_id: int, author_id: int
) -> Comment:

    print(author_id)

    await check_if_picture_exists(picture_id, db)
    picture_comments_nums_generator = (
        db.query(Comment)
        .filter(Comment.picture_id == picture_id)
        .values(Comment.picture_comment_id)
    )

    max_num = 0

    for tuple_num in picture_comments_nums_generator:
        num = tuple_num[0]
        if num > max_num:
            max_num = num

    print(f"max_num = {max_num}")

    comment = Comment(
        picture_id=picture_id,
        picture_comment_id=max_num + 1,
        text=body.text,
        user_id=author_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comments(db: Session, picture_id: int) -> List[Comment]:

    await check_if_picture_exists(picture_id, db)
    comments = (
        db.query(Comment)
        .filter(
            Comment.picture_id == picture_id,
        )
        .filter(Comment.is_deleted == False)
        .all()
    )
    return comments


async def get_comment(
    db: Session, picture_id: int, picture_comment_id: int, author_id: int
) -> Comment:
    comment = (
        db.query(Comment)
        .filter(
            Comment.picture_id == picture_id,
            Comment.picture_comment_id == picture_comment_id,
            Comment.user_id == author_id,
        )
        .filter(Comment.is_deleted == False)
        .first()
    )
    return comment


async def edit_comment(
    body: CommentBase,
    db: Session,
    picture_id: int,
    picture_comment_id: int,
    author_id: int,
) -> Comment:
    comment = await get_comment(db, picture_id, picture_comment_id, author_id)
    if comment != None:
        comment.text = body.text
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
        .filter(Comment.is_deleted == False)
        .first()
    )
    if comment != None:
        comment.is_deleted = True
        db.commit()
    return comment
