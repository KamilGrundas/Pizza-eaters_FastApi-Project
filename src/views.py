
from fastapi.security import OAuth2PasswordRequestForm
from src.repository.users_new import get_user_by_email, update_token, get_user_by_id
from src.repository.comments import get_comment
from src.services.cookie import AuthTokenMiddleware
from src.routes import comments
import asyncio
from src.services.auth_new import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import FastAPI, Form, Query
from fastapi import Request, APIRouter, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from src.schemas import CommentBase
from src.repository import pictures as pictures_repo
from src.database.db import get_db
from src.services.auth_new import get_logged_user
from fastapi import Depends, status
from src.database.models import User
from datetime import datetime


app = FastAPI()

router = APIRouter(tags=["views"])


app.add_middleware(AuthTokenMiddleware)
templates = Jinja2Templates(directory="templates")


def format_datetime(value, format='%d.%m.%Y - %H:%M:%S'):
    """Format a datetime to a different format."""
    if value is None:
        return ""
    return value.strftime(format)


templates.env.filters['datetime'] = format_datetime


@router.post("/login")
async def login(
    response: Response,
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = await get_user_by_email(body.username, db)
    if user is None or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    await update_token(user, refresh_token, db)

    # Ustawienie ciasteczek z tokenami
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        samesite="None",
        secure=True,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="None",
        secure=True,
    )


@router.get("/picture-detail/{picture_id}", response_class=HTMLResponse)
async def get_picture(
    request: Request,
    picture_id: int,
    db: Session = Depends(get_db),
    comment_text: str = Form(None),
    current_user: Optional[User] = Depends(
        get_logged_user
    ),  # Dodawanie opcjonalnego użytkownika
):
    picture = await pictures_repo.get_picture(picture_id, db)
    picture_author = await get_user_by_id(picture.user_id,db)
    picture.username = picture_author.username
    users_data = await asyncio.gather(*[get_user_by_id(comment.user_id, db) for comment in picture.comments])    
    users_dict = {user.id: user for user in users_data}
    for comment in picture.comments:
        user = users_dict.get(comment.user_id)
        if user:
            comment.username = user.username
        else:
            comment.username = "Unknown"
    context = {
        "picture": picture,
        "user": current_user,
    }

    return templates.TemplateResponse(
        "picture.html", {"request": request, "context": context}
    )


@router.get("/login", response_class=HTMLResponse,)
async def login_form(request: Request, current_user: Optional[User] = Depends(get_logged_user)):
    context = {
        "user": current_user,  # Przekazujesz użytkownika do kontekstu
    }
    if current_user:
        return RedirectResponse("/")
    return templates.TemplateResponse("login_register.html", {"request": request, "context": context})


@router.post("/logout")
async def logout(response: Response,):

    response.delete_cookie("access_token",)
    response.delete_cookie("refresh_token" )


@router.get("/upload-picture", response_class=HTMLResponse,)
async def upload_picture_form(request: Request, current_user: Optional[User] = Depends(get_logged_user)):
    context = {
        "user": current_user,  # Przekazujesz użytkownika do kontekstu
    }
    return templates.TemplateResponse("upload_picture.html", {"request": request, "context": context})


@router.get("/edit-comment/{picture_id}/{picture_comment_id}", response_class=HTMLResponse,)
async def upload_picture_form(
    request: Request,
    picture_id: int,
    picture_comment_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(
        get_logged_user
    ), 
):
    comment = await get_comment(db,picture_id,picture_comment_id,current_user.id)
    context = {
        "user": current_user,
        "comment" : comment
    }
    return templates.TemplateResponse("edit_comment.html", {"request": request, "context": context})


@router.get("/", response_class=HTMLResponse,)
async def search_pictures(
    request: Request,
    query: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(
        get_logged_user
    ), 
):
    if query:
        pictures = await pictures_repo.get_pictures_by_tags(query,db=db)
    else:
        pictures = await pictures_repo.get_pictures(db=db)

    users_data = await asyncio.gather(*[get_user_by_id(picture.user_id, db) for picture in pictures])
    
    users_dict = {user.id: user for user in users_data}
    
    for picture in pictures:
        user = users_dict.get(picture.user_id)
        if user:
            picture.username = user.username
        else:
            picture.username = "Unknown"

    context = {"pictures": pictures, "user": current_user}
    return templates.TemplateResponse("index.html", {"request": request, "context": context})


@router.get("/qr_code/{picture_id}", response_class=HTMLResponse)
async def get_qr_code(
    request: Request,
    picture_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(
        get_logged_user
    ), 
):

    picture = await pictures_repo.get_picture(picture_id, db)

    context = {
        "user": current_user,
        "picture": picture
    }
    return templates.TemplateResponse("qr_code.html", {"request": request, "context": context})


@router.get("/edit-picture/{picture_id}", response_class=HTMLResponse,)
async def upload_picture_form(
    request: Request,
    picture_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(
        get_logged_user
    ), 
):
    picture = await pictures_repo.get_picture(picture_id,db)
    context = {
        "user": current_user,
        "picture": picture
    }
    return templates.TemplateResponse("edit_picture.html", {"request": request, "context": context})
