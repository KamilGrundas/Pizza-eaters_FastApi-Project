import cloudinary
import cloudinary.uploader
import cloudinary.api


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
