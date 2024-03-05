import uvicorn
from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.database.db import get_db
from fastapi import Depends
from src.routes import auth, fake_pictures, tags
from sqlalchemy.orm import Session
from fastapi import FastAPI, File, UploadFile


app = FastAPI()


# app.include_router(image_upload.router)
app.include_router(auth.router, prefix='/api')
app.include_router(fake_pictures.router, prefix="/wizards")
app.include_router(tags.router, prefix='/wizards')


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login_register.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    pictures = fake_pictures.get_all_image_urls()
    context = {"pictures": pictures}
    return templates.TemplateResponse("index.html", {"request": request, "context": context})

@app.get("/picture-detail/", response_class=HTMLResponse)
async def get_home(request: Request):
    pictures = fake_pictures.get_all_image_urls()
    context = {"pictures": pictures}
    return templates.TemplateResponse("picture.html", {"request": request, "context": context})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
