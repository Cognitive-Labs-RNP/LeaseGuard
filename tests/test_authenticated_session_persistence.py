"""
Unit tests verifying Supabase authenticated database session persistence.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.auth import get_authenticated_user_id, get_current_user, login_user, logout_user
from services.supabase import SupabaseService


class TestAuthenticatedSessionPersistence(unittest.TestCase):
    """Test suite for user session persistence across Streamlit reruns."""

    @patch("services.auth.get_supabase_client")
    def test_login_returns_session_tokens(self, mock_client_factory):
        """Test login_user returns access_token and refresh_token from Supabase session."""
        mock_client = MagicMock()
        mock_user = MagicMock(id="user-uuid-777", email="session_user@example.com")
        mock_session = MagicMock(access_token="test-access-token-123", refresh_token="test-refresh-token-456")
        mock_response = MagicMock(user=mock_user, session=mock_session)
        mock_client.auth.sign_in_with_password.return_value = mock_response
        mock_client_factory.return_value = mock_client

        res = login_user("session_user@example.com", "ValidPassword123!")

        self.assertEqual(res["id"], "user-uuid-777")
        self.assertEqual(res["access_token"], "test-access-token-123")
        self.assertEqual(res["refresh_token"], "test-refresh-token-456")

    @patch("services.supabase.is_demo_mode", return_value=False)
    @patch("services.supabase.create_client")
    def test_supabase_service_configures_bearer_token(self, mock_create_client, mock_demo_mode):
        """Test SupabaseService configures postgrest.auth with access_token when available."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch("streamlit.session_state", {"access_token": "bearer-token-abc", "user_id": "user-uuid-777"}):
            service = SupabaseService()
            mock_client.postgrest.auth.assert_called_with("bearer-token-abc")
            self.assertEqual(service.get_current_user_id(), "user-uuid-777")

    @patch("services.demo_data.is_demo_mode", return_value=False)
    def test_logout_user_clears_session_state(self, mock_demo):
        """Test logout_user clears user_id, authenticated_user, access_token, refresh_token from session_state."""
        session_dict = {
            "authenticated_user": {"id": "user-123"},
            "user_id": "user-123",
            "access_token": "token-123",
            "refresh_token": "token-456",
        }
        with patch("streamlit.session_state", session_dict):
            with patch("services.auth.get_supabase_client"):
                logout_user()
                self.assertNotIn("authenticated_user", session_dict)
                self.assertNotIn("user_id", session_dict)
                self.assertNotIn("access_token", session_dict)
                self.assertNotIn("refresh_token", session_dict)


if __name__ == "__main__":
    unittest.main()
