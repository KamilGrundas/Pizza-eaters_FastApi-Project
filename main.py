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


# cloudinary.config(
#     cloud_name=os.getenv("CLOUD_NAME"),
#     api_key=os.getenv("API_KEY"),
#     api_secret=os.getenv("API_SECRET")
# )


@app.post("/delete_picture/")
async def delete_file(public_id: str):
    try:
        cloudinary.uploader.destroy(public_id)
        return {"message": f"Zdjęcie o public_id {public_id} zostało pomyślnie usunięte."}
    except cloudinary.api.Error as e:
        return {"error": f"Wystąpił błąd podczas usuwania zdjęcia: {e}"}


def get_download_link(public_id):
    try:
        download_url = cloudinary.utils.cloudinary_url(public_id)[0]
        return {"download_url": download_url}
    except Exception as e:
        return {"error": f"Error while generating download URL: {e}"}


@app.post("/upload_picture/")
async def upload_file(file: UploadFile = File(...), public_id: str = None):
    try:
        upload_result = cloudinary.uploader.upload(file.file, public_id=public_id)
        file_url = upload_result["secure_url"]
        return {"file_url": file_url}
    except Exception as e:
        return {"error": f"Error while uploading file: {e}"}


@app.get("/download_picture/{public_id}")
async def download_file(public_id: str):
    return get_download_link(public_id)


def apply_effect(file, public_id, effect):
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            transformation={"effect": effect}
        )
        return {"file_url": upload_result["secure_url"]}
    except Exception as e:
        return {"error": f"Error while applying effect: {e}"}


@app.put("/edit_picture/sepia/{public_id}")
async def edit_image_sepia(public_id: str, file: UploadFile = File(...)):
    return apply_effect(file.file, public_id, "sepia")


@app.put("/edit_picture/grayscale/{public_id}")
async def edit_image_grayscale(public_id: str, file: UploadFile = File(...)):
    return apply_effect(file.file, public_id, "blackwhite")


@app.put("/edit_picture/negative/{public_id}")
async def edit_image_negative(public_id: str, file: UploadFile = File(...)):
    return apply_effect(file.file, public_id, "negate")


@app.put("/edit_picture/resize/{public_id}")
async def edit_image_resize(public_id: str, file: UploadFile = File(...), width: int = 100, height: int = 100):
    transformation = {"width": width, "height": height, "crop": "fill"}
    return apply_effect(file.file, public_id, transformation)


@app.put("/edit_picture/rotate/{public_id}")
async def edit_image_rotate(public_id: str, file: UploadFile = File(...), angle: int = 90):
    transformation = {"angle": angle}
    return apply_effect(file.file, public_id, transformation)


def get_image_url(public_id):
    try:
        return {"image_url": f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error while getting image URL: {e}")


@app.get("/get_image/{public_id}")
async def get_image(public_id: str):
    return get_image_url(public_id)


def get_all_image_urls():
    try:
        result = cloudinary.api.resources(type="upload")
        images = result.get("resources", [])
        return [image["secure_url"] for image in images]
    except Exception as e:
        return {"error": f"Error while getting image URLs: {e}"}


@app.get("/get_all_images/")
async def get_images():
    return get_all_image_urls()


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
