from fastapi import HTTPException
from starlette import status
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel, UserDb


async def get_user_by_email(email: str, db: Session) -> User:

    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:

    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_user_by_username(username: str, db: Session) -> UserDb:
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def update_user_info(user_new_info: UserModel, db: Session) -> UserDb:

    user = db.query(User).filter(User.user_new_info == user_new_info).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.commit()
    db.refresh(user)

    return user


async def ban_user(username: str, db: Session) -> None:

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    db.delete(user)
    db.refresh(user)
    db.commit()


async def update_token(user: User, token: str | None, db: Session) -> None:

    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

