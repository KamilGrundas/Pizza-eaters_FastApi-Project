import pytest
from unittest.mock import MagicMock, patch
from src.services.pictures import upload_file, get_download_link, apply_effect, delete_file

# Test for upload_file function
@pytest.mark.asyncio
async def test_upload_file():
    mock_upload = MagicMock()
    mock_upload.return_value = {"secure_url": "https://example.com/image.jpg", "public_id": "12345"}
    file = MagicMock()
    file.file = "mocked_file_content"
    result = await upload_file(file)
    assert result == {"file_url": "https://example.com/image.jpg", "public_id": "12345"}

# Test for get_download_link function
@pytest.mark.asyncio
async def test_get_download_link():
    mock_cloudinary_url = MagicMock()
    mock_cloudinary_url.return_value = ("https://example.com/image.jpg",)
    result = await get_download_link("12345")
    assert result == {"download_url": "https://example.com/image.jpg"}

# Test for apply_effect function
@pytest.mark.asyncio
async def test_apply_effect():
    mock_upload = MagicMock()
    mock_upload.return_value = {"secure_url": "https://example.com/image.jpg", "public_id": "12345"}
    file = MagicMock()
    result = await apply_effect(file, "12345", "sepia")
    assert result == {"file_url": "https://example.com/image.jpg", "public_id": "12345"}

# Test for delete_file function
@pytest.mark.asyncio
async def test_delete_file():
    mock_destroy = MagicMock()
    result = await delete_file("12345")
    assert mock_destroy.assert_called_once_with("12345")
