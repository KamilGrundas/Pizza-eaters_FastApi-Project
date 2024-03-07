from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from src.schemas import UserDb, UserModel
from src.repository.users import get_user_by_username, update_user_info, ban_user
from src.services import auth
from src.database import get_db


router = APIRouter(prefix="/users", tags=["users"])
limiting = RateLimiter(times=8, seconds=60)


@router.get("/profile/{username}", response_model=UserDb)
@limiting.limit("8 per 60 seconds")
async def get_user_profile(username: str, current_user: auth.User = Depends(auth.get_current_active_user),
                           db: Session = Depends(get_db)):
    if current_user.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized!")

    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/profile", response_model=UserDb)
@limiting.limit("8 per 60 seconds")
async def get_own_profile(current_user: auth.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    user = await get_user_by_username(db, current_user.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/profile", response_model=UserDb)
@limiting.limit("8 per 60 seconds")
async def update_own_profile(
    user_info: UserModel,
    current_user: auth.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.username != user_info.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized!")

    updated_user = await update_user_info(db, user_info)
    return updated_user


@router.post("/profile/{username}/ban", response_model=UserDb)
async def ban_user_profile(username: str, current_user: auth.User = Depends(auth.get_current_user),
                           db: Session = Depends(get_db)):
    if current_user.role != auth.UserRoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Unauthorized! Only administrators can ban users.")

    banned_user = await ban_user(username, db)
    return banned_user
