import uvicorn
from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.repository import pictures as pictures_repo
from src.database.db import get_db
from src.schemas import PictureResponse

from fastapi import Depends

from src.routes import auth, tags
from src.routes import pictures as pict

from sqlalchemy.orm import Session
from fastapi import FastAPI, File, UploadFile


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



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
