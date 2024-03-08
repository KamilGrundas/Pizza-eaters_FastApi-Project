from fastapi import Depends, HTTPException, status
from src.database.models import User, Comment, Picture

from src.services.auth import get_current_user


def is_author(source: Comment | Picture, current_user: User):
    if current_user.id != source.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not an author"
        )


def get_admin(current_user: User = Depends(get_current_user)) -> User:
    # funkcja zwraca current_user, jeśli ma uprawnienia administratora, w przeciwnym wypadku rzuca wyjątek HTTP_403

    return current_user


def get_mod(current_user: User = Depends(get_current_user)) -> User:
    # funkcja zwraca current_user, jeśli ma uprawnienia moderatora lub administratora, w przeciwnym wypadku rzuca wyjątek HTTP_403

    return current_user
