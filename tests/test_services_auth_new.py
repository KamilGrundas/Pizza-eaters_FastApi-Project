import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from src.services.auth_new import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_logged_user,
    get_current_user,
    get_admin,
    get_mod,
)


class TestAuth(unittest.IsolatedAsyncioTestCase):

    async def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=15).total_seconds()

        token = await create_access_token(data, expires_delta)
        self.assertIsNotNone(token)

    async def test_create_refresh_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(days=7).total_seconds()
        token = await create_refresh_token(data, expires_delta)
        self.assertIsNotNone(token)

    async def test_decode_refresh_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(days=7).total_seconds()
        token = await create_refresh_token(data, expires_delta)
        decoded_email = await decode_refresh_token(token)
        self.assertEqual(decoded_email, "test@example.com")

    async def test_get_logged_user_valid_token(self, user):
        request = MagicMock()
        request.cookies.get.return_value = "valid_access_token"
        user = await get_logged_user(request)
        self.assertIsNotNone(user)

    async def test_get_logged_user_invalid_token(self, user):
        request = MagicMock()
        request.cookies.get.return_value = None
        user = await get_logged_user(request)
        self.assertIsNone(user)

    async def test_get_current_user_valid_token(self, user):
        request = MagicMock()
        request.cookies.get.return_value = "valid_access_token"
        with patch("src.repository.users_new.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = {"email": "test@example.com"}
            user = await get_current_user(request)
            self.assertIsNotNone(user)

    async def test_get_current_user_invalid_token(self):
        request = MagicMock()
        request.cookies.get.return_value = None
        with self.assertRaises(HTTPException) as context:
            await get_current_user(request)
        self.assertEqual(context.exception.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_admin_as_admin(self):
        user = MagicMock()
        user.role = "administrator"
        result = await get_admin(user)
        self.assertEqual(result, user)

    async def test_get_admin_as_mod(self):
        user = MagicMock()
        user.role = "moderator"
        with self.assertRaises(HTTPException) as context:
            await get_admin(user)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)

    async def test_get_admin_as_user(self):
        user = MagicMock()
        user.role = "user"
        with self.assertRaises(HTTPException) as context:
            await get_admin(user)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)

    async def test_get_mod_as_admin(self):
        user = MagicMock()
        user.role = "administrator"
        result = await get_mod(user)
        self.assertEqual(result, user)

    async def test_get_mod_as_mod(self):
        user = MagicMock()
        user.role = "moderator"
        result = await get_mod(user)
        self.assertEqual(result, user)

    async def test_get_mod_as_user(self):
        user = MagicMock()
        user.role = "user"
        with self.assertRaises(HTTPException) as context:
            await get_mod(user)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)


if __name__ == "__main__":
    unittest.main()
