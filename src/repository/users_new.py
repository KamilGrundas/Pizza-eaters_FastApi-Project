from sqlalchemy.orm import Session

from src.database.models import User, UserRoleEnum
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def get_user_by_id(id: str, db: Session) -> User:
    return db.query(User).filter(User.id == id).first()

async def create_user(body: UserModel, db: Session) -> User:

    users_num = db.query(User).count()
    print(users_num)
    new_user = User(**body.model_dump(), role=UserRoleEnum.USER)
    if users_num == 0:
        new_user.role = UserRoleEnum.ADMIN

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
