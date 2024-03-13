from typing import List

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import CommentBase, CommentResponse
from src.database.models import User, Comment, Picture

import src.repository.comments as comments_repo

from src.services.exceptions import (
    raise_404_exception_if_one_should,
    check_if_picture_exists,
)

# import src.services.auth as auth_service

from src.services import auth_new as auth_service


router = APIRouter(prefix="/{picture_id}/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_new_comment(
    picture_id: int,
    body: CommentBase,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> Comment:
    check_if_picture_exists(picture_id=picture_id, db=db)
    new_comment = await comments_repo.add_comment(body, db, picture_id, user.id)
    return new_comment


@router.get("/", response_model=List[CommentResponse])
async def get_comments(picture_id: int, db: Session = Depends(get_db)) -> List[Comment]:
    comments = await comments_repo.get_comments(db, picture_id)
    raise_404_exception_if_one_should(comments, "Comments")

    return comments


@router.get("/{picture_comment_id}", response_model=CommentResponse)
async def get_comment(
    picture_id: int,
    picture_comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    comment = await comments_repo.get_comment(
        db, picture_id, picture_comment_id, user.id
    )
    raise_404_exception_if_one_should(comment, "Comment")
    return comment


@router.put(
    "/{picture_comment_id}",
    response_model=CommentResponse,
)
async def edit_comment(
    picture_id: int,
    picture_comment_id: int,
    body: CommentBase,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> Comment:
    updated_comment = await comments_repo.edit_comment(
        body, db, picture_id, picture_comment_id, user.id
    )
    raise_404_exception_if_one_should(updated_comment, "Comment")
    return updated_comment


@router.delete(
    "/{picture_comment_id}",
    response_model=CommentResponse,
)
async def delete_comment(
    picture_id: int,
    picture_comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_mod),
) -> Comment:
    deleted_comment = await comments_repo.delete_comment(
        db, picture_id, picture_comment_id
    )
    raise_404_exception_if_one_should(deleted_comment, "Comment")
    return deleted_comment