from fastapi import Depends, APIRouter

from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Picture

from src.routes import comments

from src.conf.config import settings

from src.services.exceptions_func import no_picture_exception

router = APIRouter(prefix="/pictures", tags=["pictures"])
router.include_router(comments.router)


# to jest do zastąpienia albo rozbudowania i zmiany z fake_pictures.py na pictures.py


@router.get("/")
async def display_pictures(db: Session = Depends(get_db)):
    result = db.query(Picture).all()

    list_of_pictures_id = []
    for item in result:
        list_of_pictures_id.append(item.id)

    return {"Pictures id": list_of_pictures_id}


@router.get("/{picture_id}")
async def display_picture(picture_id: int, db: Session = Depends(get_db)):

    no_picture_exception(picture_id, db)

    comments_url = (
        f"http://{settings.host}:{settings.port}/wizards/pictures/{picture_id}/comments"
    )
    return {"picture_id": picture_id, "display comments": comments_url}


@router.post("/")
async def add_new_picture(db: Session = Depends(get_db)):

    picture = Picture()
    db.add(picture)
    db.commit()
