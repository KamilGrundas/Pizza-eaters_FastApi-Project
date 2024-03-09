from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import User
from src.repository.users import get_user_by_username, update_user_in_db
from src.schemas import UserDb, UserUpdateModel
from src.services.auth import get_current_active_user
from src.database.db import get_db


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile/{username}", response_model=UserDb)
async def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = await get_user_by_username(username=username, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/me/", response_model=UserDb)
async def get_own_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/update/{username}", response_model=UserDb)
async def update_own_profile(update_user: UserUpdateModel, current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db)):

    username = current_user.username
    if update_user.username:
        current_user.username = update_user.username

    updated_user = await update_user_in_db(username=username, new_username=update_user.username, db=db)
    return updated_user


@router.put("/admin/ban/{username}", response_model=UserDb)
async def ban_user(username: str, db: Session = Depends(get_db)):

    user = await ban_user(username=username, db=db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User {username} is already banned")

    user.is_banned = True
    db.commit()
    db.refresh(user)

    return user


