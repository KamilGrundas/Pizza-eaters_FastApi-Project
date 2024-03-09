import uvicorn
from fastapi import Depends, status
from fastapi import FastAPI, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import pictures as pictures_repo
from src.routes import auth, tags, comments
from src.routes import pictures as pict
from src.schemas import CommentBase

app = FastAPI()


# app.include_router(image_upload.router)
app.include_router(auth.router, prefix="/api")
app.include_router(pict.router, prefix="/wizards")
app.include_router(tags.router, prefix="/wizards")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login_register.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request, db: Session = Depends(get_db)):
    # zmieniłam w templatce index.html z picture na picture.url
    pictures = await pictures_repo.get_pictures(db=db)
    context = {"pictures": pictures}
    return templates.TemplateResponse(
        "index.html", {"request": request, "context": context}
    )


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
