"""
Unit and Integration Tests for Phase 5.3 End-to-End Wiring and Data Persistence.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.audit_engine import AuditEngine
from services.recovery_engine import RecoveryEngine
from services.risk_engine import RiskEngine
from services.supabase import SupabaseService


class TestEndToEndWiring(unittest.TestCase):
    """Test suite for property creation, document handling, audit execution, and recovery updates."""

    @patch("services.supabase.require_authenticated_user_id", return_value="user-uuid-999")
    def test_property_creation_schema_alignment(self, mock_user_id):
        """Test create_property maps property_code and square_footage matching SQL schema."""
        service = SupabaseService()
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_exec = MagicMock()

        payload_in = {
            "name": "Meridian Business Plaza",
            "code": "PROP-999",
            "address": "48 Crescent Avenue, Bengaluru",
            "square_feet": 35000.0,
            "status": "Active",
        }

        mock_exec.data = [{
            "id": "prop-uuid-999",
            "user_id": "user-uuid-999",
            "name": "Meridian Business Plaza",
            "property_code": "PROP-999",
            "address": "48 Crescent Avenue, Bengaluru",
            "square_footage": 35000.0,
            "status": "Active",
        }]

        mock_insert.execute.return_value = mock_exec
        mock_table.insert.return_value = mock_insert
        mock_client.table.return_value = mock_table
        service.client = mock_client

        saved = service.create_property(payload_in)

        # Verify insert payload contained SQL column names
        insert_args = mock_table.insert.call_args[0][0]
        self.assertEqual(insert_args["property_code"], "PROP-999")
        self.assertEqual(insert_args["square_footage"], 35000.0)
        self.assertEqual(insert_args["user_id"], "user-uuid-999")

        # Verify returned object normalizes both property_code/code and square_footage/square_feet
        self.assertEqual(saved["code"], "PROP-999")
        self.assertEqual(saved["square_feet"], 35000.0)

    @patch("services.supabase.require_authenticated_user_id", return_value="user-uuid-999")
    def test_save_document_strips_invalid_columns(self, mock_user_id):
        """Test save_document strips content_text from SQL payload and converts file_size to integer."""
        service = SupabaseService()
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_exec = MagicMock()

        doc_in = {
            "property_id": "prop-uuid-999",
            "document_type": "Lease Agreement",
            "filename": "Sample_Lease.pdf",
            "file_size": "1.5 MB",
            "content_text": "Section 6.1 CAM Expenses capped at $10,000",
        }

        mock_exec.data = [{
            "id": "doc-uuid-999",
            "user_id": "user-uuid-999",
            "property_id": "prop-uuid-999",
            "document_type": "Lease Agreement",
            "title": "Sample_Lease.pdf",
            "file_name": "Sample_Lease.pdf",
            "file_size": 1572864,
            "status": "Uploaded & Indexed",
        }]

        mock_insert.execute.return_value = mock_exec
        mock_table.insert.return_value = mock_insert
        mock_client.table.return_value = mock_table
        service.client = mock_client

        saved = service.save_document(doc_in)

        insert_payload = mock_table.insert.call_args[0][0]
        self.assertNotIn("content_text", insert_payload)
        self.assertEqual(insert_payload["file_name"], "Sample_Lease.pdf")
        self.assertEqual(saved["content_text"], "Section 6.1 CAM Expenses capped at $10,000")

    def test_full_audit_engine_execution_flow(self):
        """Test AuditEngine, RiskEngine, and RecoveryEngine execute deterministically end-to-end."""
        lease_data = {
            "cam_cap": 10000.0,
            "tenant_share": 15.0,
            "administrative_fee_cap_percent": 5.0,
            "expense_exclusions": ["capital repairs", "rooftop hvac"],
            "base_rent": 120000.0,
        }
        invoice_data = {
            "billed_cam_amount": 14500.0,
            "total_building_cam": 100000.0,
            "billed_tenant_share_amount": 18000.0,
            "billed_admin_fee_amount": 900.0,
            "line_items": [
                {"category": "Capital Improvements", "description": "Rooftop HVAC Repair", "billed_amount": 4200.0}
            ],
        }

        audit_engine = AuditEngine()
        audit_res = audit_engine.run_audit(lease_data, invoice_data, property_id="prop-test-01")

        self.assertGreater(audit_res["findings_count"], 0)
        self.assertGreater(audit_res["total_potential_recovery"], 0.0)

        risk_engine = RiskEngine()
        risk_res = risk_engine.calculate_lease_risk(lease_data, audit_res["findings"], property_id="prop-test-01")
        self.assertIn("overall_score", risk_res)

        rec_engine = RecoveryEngine()
        rec_rec = rec_engine.create_recovery_record(
            property_id="prop-test-01",
            claim_amount=audit_res["total_potential_recovery"],
            status="Detected",
            notes="Overcharge Identified"
        )
        self.assertEqual(rec_rec["status"], "Detected")
        self.assertEqual(rec_rec["claim_amount"], audit_res["total_potential_recovery"])


if __name__ == "__main__":
    unittest.main()
