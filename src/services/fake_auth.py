from fastapi import Depends, HTTPException, status
from src.database.models import User, Comment, Picture

from src.services.auth import get_current_user




from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
        print("We are in Auth.verify_password")
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
        print("We are in Auth.get_password_hash")

        return pwd_context.hash(password)

def create_token(data: dict, token_type: str):
        print("We are in Auth.create_token")
        to_encode = data.copy()

        if token_type == "access_token":
            expire = datetime.utcnow() + timedelta(minutes=15)
        elif token_type in ["refresh_token", "email_token"]:
            expire = datetime.utcnow() + timedelta(days=7)
        else:
            raise NameError("Given token_type is not available")

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": token_type})

        encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_token

async def decode_refresh_token(refresh_token: str):
        print("We are in Auth.decode_refresh_token")
        try:
            payload = jwt.decode(
                refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
            )
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

async def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        print("We are in Auth.get_current_user")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            print(f"\n\ntoken = {token}\n\n")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

async def get_email_from_token(token: str):
        print("We are in Auth.get_email_from_token")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )




def is_author(source: Comment | Picture, current_user: User):
    if current_user.id != source.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not an author"
        )
    return current_user


def get_admin(current_user: User = Depends(get_current_user)) -> User:
    # funkcja zwraca current_user, jeśli ma uprawnienia administratora, w przeciwnym wypadku rzuca wyjątek HTTP_403

    return current_user


def get_mod(current_user: User = Depends(get_current_user)) -> User:
    # funkcja zwraca current_user, jeśli ma uprawnienia moderatora lub administratora, w przeciwnym wypadku rzuca wyjątek HTTP_403

    return current_user
