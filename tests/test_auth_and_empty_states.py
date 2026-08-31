"""
Unit Tests for Global Authentication Protection, Auth Guard, and Empty State Behavior.
"""

import unittest
from unittest.mock import patch, MagicMock
from services.auth import require_auth, require_authenticated_user_id, logout_user
from services.supabase import SupabaseService


class TestAuthAndEmptyStates(unittest.TestCase):
    """Test suite verifying authentication guards, session management, and empty account state integrity."""

    @patch("services.auth.get_current_user")
    def test_require_auth_logged_out(self, mock_get_user):
        """Test require_auth returns None when user is logged out."""
        mock_get_user.return_value = None
        import streamlit as st
        st.session_state.pop("authenticated_user", None)
        st.session_state.pop("user_id", None)

        user = require_auth()
        self.assertIsNone(user)

    @patch("services.auth.get_current_user")
    def test_require_auth_logged_in(self, mock_get_user):
        """Test require_auth returns user dict when user is logged in."""
        mock_user = {"id": "user-uuid-1234", "email": "testuser@leaseguard.ai"}
        mock_get_user.return_value = mock_user

        user = require_auth()
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], "user-uuid-1234")
        self.assertEqual(user["email"], "testuser@leaseguard.ai")

    def test_require_authenticated_user_id_raises(self):
        """Test require_authenticated_user_id raises PermissionError when logged out."""
        import streamlit as st
        st.session_state.pop("authenticated_user", None)

        with patch("services.auth.get_current_user", return_value=None):
            with self.assertRaises(PermissionError):
                require_authenticated_user_id()

    @patch("services.auth.get_supabase_client")
    def test_logout_user_clears_session(self, mock_client_func):
        """Test logout_user triggers Supabase sign_out and handles state reset."""
        mock_client = MagicMock()
        mock_client_func.return_value = mock_client

        logout_user()
        mock_client.auth.sign_out.assert_called_once()

    @patch.object(SupabaseService, "get_current_user_id")
    def test_empty_account_behavior(self, mock_get_id):
        """Test SupabaseService returns empty lists for fresh accounts without hardcoded mock fallbacks."""
        mock_get_id.return_value = "fresh-user-uuid"

        service = SupabaseService()
        # Mock client returning empty data
        mock_table_obj = MagicMock()
        mock_select_obj = MagicMock()
        mock_eq_obj = MagicMock()
        mock_exec_obj = MagicMock()
        mock_exec_obj.data = []

        mock_eq_obj.execute.return_value = mock_exec_obj
        mock_select_obj.eq.return_value = mock_eq_obj
        mock_table_obj.select.return_value = mock_select_obj

        service.client = MagicMock()
        service.client.table.return_value = mock_table_obj

        self.assertEqual(service.get_properties(), [])
        self.assertEqual(service.get_documents(), [])
        self.assertEqual(service.get_audits(), [])
        self.assertEqual(service.get_findings(), [])
        self.assertEqual(service.get_risk_scores(), [])
        self.assertEqual(service.get_recovery_records(), [])

    @patch.object(SupabaseService, "get_current_user_id")
    def test_save_document(self, mock_get_id):
        """Test SupabaseService save_document attaches user_id and saves record."""
        mock_get_id.return_value = "test-user-123"
        service = SupabaseService()

        doc_data = {
            "property_id": "prop-111",
            "document_type": "Lease Agreement",
            "filename": "Test_Lease.pdf",
            "file_size": "1.5 MB"
        }

        mock_table_obj = MagicMock()
        mock_insert_obj = MagicMock()
        mock_exec_obj = MagicMock()
        mock_exec_obj.data = [{**doc_data, "user_id": "test-user-123", "id": "doc-uuid-1"}]

        mock_insert_obj.execute.return_value = mock_exec_obj
        mock_table_obj.insert.return_value = mock_insert_obj
        service.client = MagicMock()
        service.client.table.return_value = mock_table_obj

        saved = service.save_document(doc_data)
        self.assertEqual(saved["property_id"], "prop-111")
        self.assertEqual(saved["user_id"], "test-user-123")


if __name__ == "__main__":
    unittest.main()
