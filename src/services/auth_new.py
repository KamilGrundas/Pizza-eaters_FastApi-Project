from typing import Optional


from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users_new as repository_users
from src.database.models import User, UserRoleEnum


from src.conf.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


# define a function to generate a new refresh token
async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update(
        {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
    )
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def decode_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["scope"] == "refresh_token":
            email = payload["sub"]
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid scope for token",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_logged_user(request: Request, db: Session = Depends(get_db)):
    user = "User"
    token_cookie = request.cookies.get("access_token")

    if not token_cookie:
        user = None
    try:
        # Decode JWT
        payload = jwt.decode(token_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            user = None
    except JWTError:
        user = None
    except:
        user = None

    if not user == None:
        user = await repository_users.get_user_by_email(email, db)

    return user


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_cookie = request.cookies.get("access_token")

    if not token_cookie:
        raise credentials_exception
    try:
        # Decode JWT
        payload = jwt.decode(token_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user


async def get_admin(user: User = Depends(get_current_user)):
    if user.role == UserRoleEnum.ADMIN:
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def get_mod(user: User = Depends(get_current_user)):
    if user.role in [UserRoleEnum.ADMIN, UserRoleEnum.MOD]:
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
