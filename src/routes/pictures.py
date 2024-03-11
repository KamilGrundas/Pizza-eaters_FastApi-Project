from fastapi import Depends, APIRouter, File, UploadFile, HTTPException, status, Query
import cloudinary
import cloudinary.uploader
import cloudinary.api
from qrcode.main import QRCode
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Picture, Tag, User

import qrcode
from src.routes import comments
from src.schemas import QRCodeRequest, PictureResponse, PictureResponseDetails

from src.conf.config import settings

from src.services.exceptions import (
    raise_404_exception_if_one_should,
    check_if_picture_exists,
    check_if_tag_exists,
    check_if_comment_exists,
)
from src.services import pictures as pictures_service

from src.repository import pictures as pictures_repo
from src.repository import comments as comments_repo
from src.repository import tags as tags_repo

from src.services import auth_new as auth_service

from src.services.exceptions import (
    TAG_IS_ALREADY_ASSIGNED_TO_PICTURE,
    PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED,
    TAG_IS_NOT_ASSIGNED_TO_PICTURE,
    TAG_IS_ALREADY_ASSIGNED_TO_PICTURE_AND_PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED,
)

from typing import List


router = APIRouter(prefix="/pictures", tags=["pictures"])
router.include_router(comments.router)


@router.post("/upload_picture/", response_model=PictureResponse)
async def upload_image_mod(
    file: UploadFile = File(...),
    color_mod: str | None = Query(
        default=None, description="e.g.: sepia, blackwhite, negate, blur grayscale"
    ),
     crop: str | None = Query(
            default="fill", description="e.g.: fill, fit, scale"
     ),
     
    width: int | None = None,
    height: int | None = None,
    radius: int | None = None,
    description: str = None,
    public_id: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> PictureResponse:
    transformation = pictures_service.make_transformation(
        color_mod=color_mod, width=width, height=height, crop=crop, radius=radius
    )
    cloudinary_result = await pictures_service.apply_effects(
        file.file, public_id, transformation
    )

    try:
        file_url = cloudinary_result["file_url"]
        public_id = cloudinary_result["public_id"]
    except:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY)

    picture = await pictures_repo.add_picture(
        url=file_url,
        public_id=public_id,
        description=description,
        db=db,
        author_id=user.id,
    )
    return picture


@router.get("/{picture_id}", response_model=PictureResponse)
async def get_picture(picture_id: int, db: Session = Depends(get_db)):
    picture = await pictures_repo.get_picture(picture_id=picture_id, db=db)
    raise_404_exception_if_one_should(picture, "Picture")
    return picture


@router.get("/{picture_id}/details", response_model=PictureResponseDetails)
async def get_picture_details(picture_id: int, db: Session = Depends(get_db)):
    picture = await pictures_repo.get_picture(picture_id=picture_id, db=db)
    raise_404_exception_if_one_should(picture, "Picture")
    return picture


@router.get("/", response_model=List[PictureResponse])
async def display_pictures(db: Session = Depends(get_db)):
    result = db.query(Picture).all()
    return result


@router.put("/{picture_id}", response_model=PictureResponse)
async def edit_description(
    picture_id: int,
    new_description: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    database_result = await pictures_repo.edit_picture_description(
        picture_id=picture_id, db=db, new_description=new_description, author_id=user.id
    )
    raise_404_exception_if_one_should(database_result, "Picture")

    return database_result


@router.delete("/{picture_id}", response_model=PictureResponse)
async def delete_file(
    picture_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    picture = await pictures_repo.get_picture(picture_id=picture_id, db=db)
    raise_404_exception_if_one_should(picture, "Picture")
    public_id = picture.public_id
    cloudinary_result = await pictures_service.delete_file(public_id)
    database_result = await pictures_repo.delete_picture(
        picture_id=picture_id, db=db, author_id=user.id
    )

    return database_result


@router.put("/{picture_id}/add_tag")
async def edit_description(picture_id: int, tag_id: int, db: Session = Depends(get_db)):

    check_if_picture_exists(picture_id=picture_id, db=db)
    check_if_tag_exists(tag_id=tag_id, db=db)

    database_result = await pictures_repo.add_tag(picture_id, tag_id, db)

    if database_result == -3:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is already added to picture and picture has already 5 tags assigned",
        )

    if database_result == TAG_IS_ALREADY_ASSIGNED_TO_PICTURE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is already assigned to picture.",
        )

    if database_result == PICTURE_HAS_ALREADY_5_TAGS_ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Picture has already five tags assigned",
        )

    return "ok"


@router.put("/{picture_id}/delete_tag")
async def edit_description(picture_id: int, tag_id: int, db: Session = Depends(get_db)):

    check_if_picture_exists(picture_id=picture_id, db=db)
    check_if_tag_exists(tag_id=tag_id, db=db)

    database_result = await pictures_repo.delete_tag(picture_id, tag_id, db)

    if database_result == 0:
        return "ok"

    if database_result == TAG_IS_NOT_ASSIGNED_TO_PICTURE:
        return "Tag is not assigned to picture"


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
