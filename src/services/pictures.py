import cloudinary
import cloudinary.uploader
import cloudinary.api
from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.cloud_name,
    api_key=settings.api_key,
    api_secret=settings.api_secret,
)


def get_url_and_public_id(upload_result: dict) -> dict:
    return {
        "file_url": upload_result["secure_url"],
        "public_id": upload_result["public_id"],
    }


async def upload_file(file, public_id=None) -> dict:
    try:
        upload_result = cloudinary.uploader.upload(file.file, public_id=public_id)
        return get_url_and_public_id(upload_result)
    except Exception as e:
        return {"error": f"Error while uploading file: {e}"}


async def get_download_link(public_id):
    try:
        download_url = cloudinary.utils.cloudinary_url(public_id)[0]
        return {"download_url": download_url}
    except Exception as e:
        return {"error": f"Error while generating download URL: {e}"}


async def apply_effect(file, public_id, effect) -> dict:
    try:
        upload_result = cloudinary.uploader.upload(
            file, public_id=public_id, transformation={"effect": effect}
        )
        return get_url_and_public_id(upload_result)
    except Exception as e:

        return {"error": f"Error while applying effect: {e}"}


async def delete_file(public_id: str) -> dict:
    try:
        cloudinary.uploader.destroy(public_id)
        return {
            "message": f"Zdjęcie o public_id {public_id} zostało pomyślnie usunięte."
        }
    except cloudinary.api.Error as e:
        return {"error": f"Wystąpił błąd podczas usuwania zdjęcia: {e}"}


def make_transformation(color_mod, width, height, angle):

    transformations = []

    if width != None and height != None:
        transformations.append({"width": width, "height": height, "crop": "fill"})
    if angle != None:
        transformations.append({"angle": angle})
    if color_mod in [
        "sepia",
        "blackwhite",
        "negate",
    ]:
        transformations.append({"effect": color_mod})

    print(transformations)
    return transformations


async def apply_effects(file, public_id, transformations) -> dict:

    upload_result = cloudinary.uploader.upload(
        file, public_id=public_id, transformation=transformations
    )
    return get_url_and_public_id(upload_result)
#
