import pytest
from unittest.mock import MagicMock, patch
from src.services.pictures import (
    get_url_and_public_id,
    upload_file,
    get_download_link,
    apply_effect,
    delete_file,
)

def test_get_url_and_public_id():
    upload_result = {"secure_url": "https://example.com/image.jpg", "public_id": "12345"}
    expected_result = {"file_url": "https://example.com/image.jpg", "public_id": "12345"}
    assert get_url_and_public_id(upload_result) == expected_result

@patch('your_module.cloudinary.uploader.upload')
def test_upload_file(mock_upload):
    mock_upload.return_value = {"secure_url": "https://example.com/image.jpg", "public_id": "12345"}
    file = MagicMock()
    file.file = "mocked_file_content"
    assert upload_file(file) == {"file_url": "https://example.com/image.jpg", "public_id": "12345"}

@patch('your_module.cloudinary.utils.cloudinary_url')
def test_get_download_link(mock_cloudinary_url):
    mock_cloudinary_url.return_value = ("https://example.com/image.jpg",)
    assert get_download_link("12345") == {"download_url": "https://example.com/image.jpg"}

@patch('your_module.cloudinary.uploader.upload')
def test_apply_effect(mock_upload):
    mock_upload.return_value = {"secure_url": "https://example.com/image.jpg", "public_id": "12345"}
    file = MagicMock()
    assert apply_effect(file, "12345", "sepia") == {"file_url": "https://example.com/image.jpg", "public_id": "12345"}

@patch('your_module.cloudinary.uploader.destroy')
def test_delete_file(mock_destroy):
    delete_file("12345")
    mock_destroy.assert_called_once_with("12345")



