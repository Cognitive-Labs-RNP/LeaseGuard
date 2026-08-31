"""
Unit Tests for Supabase Registration & Login Error Handling.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.auth import login_user, register_user


class TestRegistrationErrorHandling(unittest.TestCase):
    """Test suite for authentication exception handling and flow validation."""

    def test_register_invalid_email_format(self):
        """Test register_user rejects invalid email address before API call."""
        with self.assertRaises(ValueError) as ctx:
            register_user("invalid-email-address", "ValidPassword123!")
        self.assertIn("Please enter a valid email address", str(ctx.exception))

    def test_register_weak_password_length(self):
        """Test register_user rejects passwords under 6 characters."""
        with self.assertRaises(ValueError) as ctx:
            register_user("user@example.com", "12345")
        self.assertIn("at least 6 characters", str(ctx.exception))

    @patch("services.auth.get_supabase_client")
    def test_register_rate_limit_429(self, mock_client_factory):
        """Test HTTP 429 / email rate limit raises RuntimeError with exact required message."""
        mock_client = MagicMock()
        mock_error = Exception("HTTPStatusError 429 Client Error: Too Many Requests for url")
        mock_error.status = 429
        mock_error.code = "over_email_send_rate_limit"
        mock_error.message = "email rate limit exceeded"
        mock_client.auth.sign_up.side_effect = mock_error
        mock_client_factory.return_value = mock_client

        with self.assertRaises(RuntimeError) as ctx:
            register_user("rate_limit_user@example.com", "ValidPass123!")

        self.assertEqual(
            str(ctx.exception),
            "Too many signup attempts. Supabase's email rate limit has been reached. Please wait and try again later."
        )

    @patch("services.auth.get_supabase_client")
    def test_register_user_already_exists(self, mock_client_factory):
        """Test duplicate user registration raises ValueError with exact required message."""
        mock_client = MagicMock()
        mock_error = Exception("User already registered")
        mock_error.status = 400
        mock_error.code = "user_already_exists"
        mock_error.message = "User already registered"
        mock_client.auth.sign_up.side_effect = mock_error
        mock_client_factory.return_value = mock_client

        with self.assertRaises(ValueError) as ctx:
            register_user("existing_user@example.com", "ValidPass123!")

        self.assertEqual(
            str(ctx.exception),
            "This email is already registered. Please log in instead."
        )

    @patch("services.auth.get_supabase_client")
    def test_register_requires_email_confirmation(self, mock_client_factory):
        """Test signup succeeding with session=None sets requires_confirmation=True."""
        mock_client = MagicMock()
        mock_user = MagicMock(id="unconfirmed-user-uuid", email="newuser@example.com")
        mock_response = MagicMock(user=mock_user, session=None)
        mock_client.auth.sign_up.return_value = mock_response
        mock_client_factory.return_value = mock_client

        res = register_user("newuser@example.com", "ValidPass123!")

        self.assertTrue(res.get("requires_confirmation"))
        self.assertIsNone(res.get("session"))
        self.assertEqual(res.get("id"), "unconfirmed-user-uuid")

    @patch("services.auth.get_supabase_client")
    def test_register_instant_session_success(self, mock_client_factory):
        """Test signup with active session returns requires_confirmation=False."""
        mock_client = MagicMock()
        mock_user = MagicMock(id="active-user-uuid", email="active@example.com")
        mock_session = MagicMock(access_token="token-abc-123")
        mock_response = MagicMock(user=mock_user, session=mock_session)
        mock_client.auth.sign_up.return_value = mock_response
        mock_client_factory.return_value = mock_client

        res = register_user("active@example.com", "ValidPass123!")

        self.assertFalse(res.get("requires_confirmation"))
        self.assertIsNotNone(res.get("session"))
        self.assertEqual(res.get("id"), "active-user-uuid")

    @patch("services.auth.get_supabase_client")
    def test_login_email_not_confirmed(self, mock_client_factory):
        """Test login failing due to email not confirmed raises RuntimeError."""
        mock_client = MagicMock()
        mock_error = Exception("Email not confirmed")
        mock_error.status = 400
        mock_error.code = "email_not_confirmed"
        mock_error.message = "Email not confirmed"
        mock_client.auth.sign_in_with_password.side_effect = mock_error
        mock_client_factory.return_value = mock_client

        with self.assertRaises(RuntimeError) as ctx:
            login_user("unconfirmed@example.com", "ValidPass123!")

        self.assertIn("not been confirmed yet", str(ctx.exception))

    @patch("services.auth.get_supabase_client")
    def test_login_invalid_credentials(self, mock_client_factory):
        """Test login with wrong password raises ValueError."""
        mock_client = MagicMock()
        mock_error = Exception("Invalid login credentials")
        mock_error.status = 400
        mock_error.code = "invalid_credentials"
        mock_error.message = "Invalid login credentials"
        mock_client.auth.sign_in_with_password.side_effect = mock_error
        mock_client_factory.return_value = mock_client

        with self.assertRaises(ValueError) as ctx:
            login_user("existing@example.com", "WrongPassword123!")

        self.assertEqual(
            str(ctx.exception),
            "Invalid email or password. Please check your credentials and try again."
        )


if __name__ == "__main__":
    unittest.main()
