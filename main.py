import uvicorn
from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.database.db import get_db
from fastapi import Depends
from src.routes import fake_pictures  # tags
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import FastAPI, File, UploadFile
from dotenv import load_dotenv
import os

load_dotenv()
cloud_name = os.getenv("CLOUD_NAME")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
postgres_db = os.getenv("POSTGRES_DB")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_port = os.getenv("POSTGRES_PORT")

app = FastAPI()


# app.include_router(image_upload.router)

app.include_router(fake_pictures.router, prefix="/wizards")

# app.include_router(tags.router, prefix='/wizards')

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login_register.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request, db: Session = Depends(get_db)):
    pictures =  await fake_pictures.display_pictures(db)
    context = {"pictures" : pictures}
    return templates.TemplateResponse("index.html", {"request": request, "context":context})


cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
