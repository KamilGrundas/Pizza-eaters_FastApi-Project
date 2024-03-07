from fastapi import Depends, APIRouter, File, UploadFile, HTTPException, status, Query
import cloudinary
import cloudinary.uploader
import cloudinary.api
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Picture, QRCode

import qrcode
from src.routes import comments
from src.schemas import (
    QRCodeRequest,
    PictureResponse,
    PictureResponseDetails,
    Comment2Display,
)

from src.conf.config import settings

from src.services.exceptions_func import no_comment_exception, no_picture_exception
from src.services import pictures as pictures_service

from src.repository import pictures as pictures_repo
from src.repository import comments as comments_repo
from src.repository import tags as tags_repo

from typing import List

cloud_name = settings.cloud_name
api_key = settings.api_key
api_secret = settings.api_secret

cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)

router = APIRouter(prefix="/pictures", tags=["pictures"])
router.include_router(comments.router)


@router.post("/upload_picture/", response_model=PictureResponse)
async def upload_image_mod(
    file: UploadFile = File(...),
    color_mod: str | None = Query(
        default=None, description="e.g.: sepia, blackwhite, negate"
    ),
    width: int | None = None,
    height: int | None = None,
    angle: int | None = None,
    description: str = None,
    public_id: str = None,
    db: Session = Depends(get_db),
) -> PictureResponse:
    transformation = pictures_service.make_transformation(
        color_mod=color_mod, width=width, height=height, angle=angle
    )
    cloudinary_result = await pictures_service.apply_effects(
        file.file, public_id, transformation
    )
    database_result = await pictures_repo.copy_picture_from_cloudinary_to_database(
        cloudinary_result, description, db
    )
    return database_result


@router.get("/{picture_id}", response_model=PictureResponse)
async def picture_details(picture_id: int, db: Session = Depends(get_db)):
    no_picture_exception(picture_id=picture_id, db=db)
    picture = await pictures_repo.get_picture(picture_id=picture_id, db=db)
    return picture


@router.get("/{picture_id}/details", response_model=PictureResponseDetails)
async def picture_details(picture_id: int, db: Session = Depends(get_db)):
    no_picture_exception(picture_id=picture_id, db=db)
    picture = await pictures_repo.get_picture(picture_id=picture_id, db=db)

    return picture


@router.get("/", response_model=List[PictureResponse])
async def display_pictures(db: Session = Depends(get_db)):
    result = db.query(Picture).all()

    return result


@router.delete("/{picture_id}", response_model=PictureResponse)
async def delete_file(picture_id: int, db: Session = Depends(get_db)):

    no_picture_exception(picture_id=picture_id, db=db)
    picture = await pictures_repo.get_picture(picture_id=picture_id, db=db)
    public_id = picture.public_id
    cloudinary_result = await pictures_service.delete_file(public_id)
    database_result = await pictures_repo.delete_picture(picture_id=picture_id, db=db)

    return database_result


@router.put("/{picture_id}", response_model=PictureResponse)
async def edit_description(
    picture_id: int,
    new_description: str,
    db: Session = Depends(get_db),
):

    no_picture_exception(picture_id=picture_id, db=db)
    database_result = await pictures_repo.edit_picture_description(
        picture_id=picture_id, db=db, new_description=new_description
    )

    return database_result


# te rzeczy poniżej też trzeba jakoś podłączyć do reszty ale to zaraz


@router.post("/generate_qr_code/")
async def generate_qr_code(
    qr_code_request: QRCodeRequest, db: Session = Depends(get_db)
):
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


# #


# def get_download_link(public_id):
#     try:
#         download_url = cloudinary.utils.cloudinary_url(public_id)[0]
#         return {"download_url": download_url}
#     except Exception as e:
#         return {"error": f"Error while generating download URL: {e}"}


# @router.get("/download_picture/{public_id}")
# async def download_file(public_id: str):
#     return get_download_link(public_id)


# # przeniesiona do services
# def apply_effect(file, public_id, effect):
#     try:
#         upload_result = cloudinary.uploader.upload(
#             file, public_id=public_id, transformation={"effect": effect}
#         )
#         return {"file_url": upload_result["secure_url"]}
#     except Exception as e:
#         return {"error": f"Error while applying effect: {e}"}


# # @router.get("/get_all_images/")
# async def get_images():
#     return get_all_image_urls()


# # @router.put("/edit_picture/sepia/{public_id}")
# async def edit_image_sepia(public_id: str, file: UploadFile = File(...)):
#     return apply_effect(file.file, public_id, "sepia")


# # @router.put("/edit_picture/grayscale/{public_id}")
# async def edit_image_grayscale(public_id: str, file: UploadFile = File(...)):
#     return apply_effect(file.file, public_id, "blackwhite")


# # @router.put("/edit_picture/negative/{public_id}")
# async def edit_image_negative(public_id: str, file: UploadFile = File(...)):
#     return apply_effect(file.file, public_id, "negate")


# # @router.put("/edit_picture/resize/{public_id}")
# async def edit_image_resize(
#     public_id: str, file: UploadFile = File(...), width: int = 100, height: int = 100
# ):
#     transformation = {"width": width, "height": height, "crop": "fill"}
#     return apply_effect(file.file, public_id, transformation)


# # @router.put("/edit_picture/rotate/{public_id}")
# async def edit_image_rotate(
#     public_id: str, file: UploadFile = File(...), angle: int = 90
# ):
#     transformation = {"angle": angle}
#     return apply_effect(file.file, public_id, transformation)


# def get_image_url(public_id):
#     try:
#         return {
#             "image_url": f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=404, detail=f"Error while getting image URL: {e}"
#         )


# # @router.get("/get_image/{public_id}")
# async def get_image(public_id: str, db: Session = Depends(get_db)):
#     return get_image_url(public_id)


# def get_all_image_urls():
#     try:
#         result = cloudinary.api.resources(type="upload")
#         images = result.get("resources", [])
#         return [image["secure_url"] for image in images]
#     except Exception as e:
#         return {"error": f"Error while getting image URLs: {e}"}
