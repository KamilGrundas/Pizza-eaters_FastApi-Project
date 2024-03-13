import unittest
from unittest.mock import AsyncMock, patch
from fastapi_mail.errors import ConnectionErrors
from src.services.send_verification_email import send_email


class TestSendEmail(unittest.IsolatedAsyncioTestCase):

    async def test_send_email_success(self):

        mock_fastmail = AsyncMock()
        with patch('src.services.send_verification_email.FastMail', return_value=mock_fastmail):
            await send_email("test@example.com", "test_user", "example.com")

        mock_fastmail.send_message.assert_called_once()
        args, kwargs = mock_fastmail.send_message.call_args
        message = args[0]
        self.assertEqual(message.subject, "Confirm your email")
        self.assertEqual(message.recipients, ["test@example.com"])
        self.assertEqual(message.subtype, "html")
        self.assertEqual(kwargs["template_name"], "verification_email.html")

    async def test_send_email_connection_error(self):

        mock_fastmail = AsyncMock()
        mock_fastmail.send_message.side_effect = ConnectionErrors("Connection failed")

        with patch('src.services.send_verification_email.FastMail', return_value=mock_fastmail):
            with self.assertRaises(ConnectionErrors):
                await send_email("test@example.com", "test_user", "example.com")


if __name__ == "__main__":
    unittest.main()
