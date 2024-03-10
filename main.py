import uvicorn
from fastapi import Request, APIRouter, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from src.schemas import CommentBase, CommentResponse
from src.repository import pictures as pictures_repo
from src.database.db import get_db
from src.schemas import PictureResponse
from src.services.auth_new import get_logged_user
from fastapi import Depends, status
from src.database.models import User
from src.routes import auth, tags, comments, auth_new
from src.routes import pictures as pict
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import FastAPI, File, UploadFile, Form
from src.services.auth_new import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from fastapi.security import OAuth2PasswordRequestForm
from src.repository.users_new import get_user_by_email, update_token, get_user_by_id
from src.services.cookie import AuthTokenMiddleware
import asyncio


app = FastAPI()


# app.include_router(image_upload.router)
# app.include_router(auth.router, prefix="/api")
app.include_router(pict.router, prefix="/wizards")
app.include_router(tags.router, prefix="/wizards")
app.include_router(auth_new.router, prefix="/api")
app.add_middleware(AuthTokenMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(key="mycookie", value="value_of_cookie")
    return {"message": "Cookie has been set"}


# @app.get("/login/", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login_register.html", {"request": request})


@app.post("/login")
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

    # Przekierowanie po pomyślnym logowaniu
    return {"message": "Logged in"}


@app.get("/", response_class=HTMLResponse)
async def get_home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_logged_user),
):
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


@app.post("/picture-detail/{picture_id}", status_code=status.HTTP_201_CREATED)
@app.get("/picture-detail/{picture_id}", response_class=HTMLResponse)
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
        user = users_dict.get(picture.user_id)
        if user:
            comment.username = user.username
        else:
            comment.username = "Unknown"
    context = {
        "picture": picture,
        "user": current_user,  # Przekazujesz użytkownika do kontekstu
    }
    if request.method == "POST" and comment_text:
        # Przy dodawaniu komentarza, sprawdzasz, czy użytkownik jest zalogowany
        if current_user:
            await comments.add_new_comment(
                picture_id, CommentBase(text=comment_text), db, current_user
            )
        else:
            raise HTTPException(
                status_code=401, detail="You have to log in to comment."
            )
    return templates.TemplateResponse(
        "picture.html", {"request": request, "context": context}
    )

@app.get("/register/", response_class=HTMLResponse)
async def get_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse,)
async def login_form(request: Request, current_user: Optional[User] = Depends(get_logged_user)):
    context = {
        "user": current_user,  # Przekazujesz użytkownika do kontekstu
    }
    if current_user:
        return RedirectResponse("/")
    return templates.TemplateResponse("login_register.html", {"request": request, "context": context})

@app.get("/logout")
async def logout(response: Response,):

    response.delete_cookie("access_token",)
    response.delete_cookie("refresh_token" )
    return {"message": "Logged out"}



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
