import uvicorn
from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.schemas import CommentBase, CommentResponse
from src.repository import pictures as pictures_repo
from src.database.db import get_db
from src.schemas import PictureResponse

from fastapi import Depends, status
from src.services.auth import get_current_user, verify_jwt_token, verify_token
from src.routes import auth, tags, comments
from src.routes import pictures as pict
from src.repository.users import get_user_by_email
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import FastAPI, File, UploadFile, Form


app = FastAPI()


# app.include_router(image_upload.router)
app.include_router(auth.router, prefix="/api")
app.include_router(pict.router, prefix="/wizards")
app.include_router(tags.router, prefix="/wizards")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    context = None
    return templates.TemplateResponse("login_register.html", {"request": request, "context": context})


# @app.get("/", response_class=HTMLResponse)
# async def get_home(request: Request, user_payload: Optional[dict] = Depends(verify_jwt_token), db: Session = Depends(get_db)):
#     pictures = await pictures_repo.get_pictures(db=db)
#     if not user_payload is None:
#         email = user_payload["sub"]
#         user = await get_user_by_email(email, db)
#         context = {"pictures": pictures, user:"user"}
#         print(user)
        
#     else:
#         user = None
#         context = {"pictures": pictures}

    
#     return templates.TemplateResponse(
#         "index.html", {"request": request, "context": context}
#     )

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request, user_payload: Optional[dict] = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    pictures = await pictures_repo.get_pictures(db=db)  # Przykład, załóżmy, że to jest wynik z bazy danych
    user = None
    if user_payload:
        email = user_payload["sub"]
        user = await get_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")  # Dodaj obsługę, jeśli użytkownik nie zostanie znaleziony
        context = {"request": request, "pictures": pictures, "user": user}
    else:
        context = {"request": request, "pictures": pictures, "user": user}
    template = "index.html"
    return templates.TemplateResponse(template, context)

@app.post("/picture-detail/{picture_id}", status_code=status.HTTP_201_CREATED)
@app.get("/picture-detail/{picture_id}", response_class=HTMLResponse)
async def get_picture(
    request: Request,
    picture_id: int,
    db: Session = Depends(get_db),
    comment_text: str = Form(None),
):
    picture = await pictures_repo.get_picture(picture_id, db)
    context = {"picture": picture}
    if request.method == "POST" and comment_text:
        await comments.add_new_comment(picture_id, CommentBase(text=comment_text), db)
    return templates.TemplateResponse(
        "picture.html", {"request": request, "context": context}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
