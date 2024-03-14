from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


@patch("app.templates.TemplateResponse")
@patch("app.pictures_repo.get_picture")
def test_get_qr_code(mock_get_picture, mock_template_response):
    picture_id = 1
    request = MagicMock()
    db = MagicMock()
    current_user = MagicMock()
    picture = {"id": picture_id, "url": "http://example.com/picture.png"}
    mock_get_picture.return_value = picture

    response = client.get(f"/qr_code/{picture_id}")

    mock_get_picture.assert_called_once_with(picture_id, db)
    mock_template_response.assert_called_once_with(
        "qr_code.html", {"request": request, "context": {"user": current_user, "picture": picture}}
    )
    assert response.status_code == 200
