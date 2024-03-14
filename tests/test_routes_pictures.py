from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


@patch("app.db", MagicMock())
@patch("app.cloudinary.uploader.upload", MagicMock(return_value={"secure_url": "http://example.com/qr_code.png"}))
def test_generate_qr_code():
    class MockQRCodeRequest:
        def __init__(self, picture_url):
            self.picture_url = picture_url


    with patch("app.Picture") as mock_picture:
        mock_picture.return_value.qr_url = None
        mock_picture_instance = mock_picture.query().filter().first.return_value
        mock_picture_instance.qr_url = None
        response = client.post("/generate_qr_code/", json={"picture_url": "http://example.com/picture.png"})
        assert response.status_code == 200
        assert response.json() == {"picture_id": mock_picture_instance.id}

    with patch("app.Picture") as mock_picture:
        mock_picture.query().filter().first.return_value = None
        response = client.post("/generate_qr_code/", json={"picture_url": "http://example.com/non_existing_picture.png"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Picture not found"}

    with patch("app.Picture") as mock_picture:
        mock_picture_instance = mock_picture.query().filter().first.return_value
        mock_picture_instance.qr_url = "http://example.com/qr_code.png"
        response = client.post("/generate_qr_code/", json={"picture_url": "http://example.com/picture.png"})
        assert response.status_code == 200
        assert response.json() == {"picture_id": mock_picture_instance.id}