from fastapi import Depends, APIRouter, File, UploadFile, HTTPException
import cloudinary
import cloudinary.uploader
import cloudinary.api
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Picture, QRCode

import qrcode
from src.routes import comments
from src.schemas import QRCodeRequest

from src.conf.config import settings

from src.services.exceptions_func import no_picture_exception

cloud_name = settings.cloud_name
api_key = settings.api_key
api_secret = settings.api_secret

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

router = APIRouter(prefix="/pictures", tags=["pictures"])
router.include_router(comments.router)


# to jest do zastąpienia albo rozbudowania i zmiany z fake_pictures.py na pictures.py

async def display_pictures(db: Session = Depends(get_db)):
    result = db.query(Picture).all()

    list_of_pictures_id = []
    for item in result:
        list_of_pictures_id.append(item.id)

    return {"Pictures id": list_of_pictures_id}


@router.post("/delete_picture/")
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


@router.post("/upload_picture/")
async def upload_file(file: UploadFile = File(...), public_id: str = None):
    try:
        upload_result = cloudinary.uploader.upload(file.file, public_id=public_id)
        file_url = upload_result["secure_url"]
        return {"file_url": file_url}
    except Exception as e:
        return {"error": f"Error while uploading file: {e}"}


@router.get("/download_picture/{public_id}")
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


@router.get("/get_image/{public_id}")
async def get_image(public_id: str):
    return get_image_url(public_id)


def get_all_image_urls():
    try:
        result = cloudinary.api.resources(type="upload")
        images = result.get("resources", [])
        return [image["secure_url"] for image in images]
    except Exception as e:
        return {"error": f"Error while getting image URLs: {e}"}


@router.get("/get_all_images/")
async def get_images():
    return get_all_image_urls()


@router.put("/edit_picture/sepia/{public_id}")
async def edit_image_sepia(public_id: str, file: UploadFile = File(...)):
    return apply_effect(file.file, public_id, "sepia")


@router.put("/edit_picture/grayscale/{public_id}")
async def edit_image_grayscale(public_id: str, file: UploadFile = File(...)):
    return apply_effect(file.file, public_id, "blackwhite")


@router.put("/edit_picture/negative/{public_id}")
async def edit_image_negative(public_id: str, file: UploadFile = File(...)):
    return apply_effect(file.file, public_id, "negate")


@router.put("/edit_picture/resize/{public_id}")
async def edit_image_resize(public_id: str, file: UploadFile = File(...), width: int = 100, height: int = 100):
    transformation = {"width": width, "height": height, "crop": "fill"}
    return apply_effect(file.file, public_id, transformation)


@router.put("/edit_picture/rotate/{public_id}")
async def edit_image_rotate(public_id: str, file: UploadFile = File(...), angle: int = 90):
    transformation = {"angle": angle}
    return apply_effect(file.file, public_id, transformation)


def get_image_url(public_id):
    try:
        return {"image_url": f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error while getting image URL: {e}")


@router.post("/generate_qr_code/")
async def generate_qr_code(qr_code_request: QRCodeRequest, db: Session = Depends(get_db)):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_code_request.transformed_photo_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    qr_img_path = f"qr_codes/{qr_code_request.transformed_photo_url.replace('/', '_').replace(':', '_')}.png"
    qr_img.save(qr_img_path)

    # Save QR code URL to the database
    qr_code = QRCode(url=qr_img_path)
    db.add(qr_code)
    db.commit()

    return {"qr_code_url": qr_img_path}


@router.get("/qr_code/{qr_code_id}")
async def get_qr_code(qr_code_id: int, db: Session = Depends(get_db)):
    qr_code = db.query(QRCode).filter(QRCode.id == qr_code_id).first()
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    return qr_code.url
