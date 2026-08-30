"""
Unit and Fallback Tests for Lease Extraction AI Pipeline (Phase 3).
"""
import unittest
from unittest.mock import AsyncMock, patch
from services.ai import extract_lease_rules, LeaseRules


SAMPLE_LEASE_TEXT = """
ABC Retail Lease has a base annual rent of $120,000.
CAM expenses are capped at $10,000 per year.
The tenant is responsible for 15% of applicable CAM expenses.
Administrative fees may not exceed 5% of CAM expenses.
The landlord must provide an annual CAM reconciliation.
"""


class TestLeaseExtractionPipeline(unittest.TestCase):
    """Test suite for Lease Extraction pipeline schema validation and fallback behavior."""

    def test_pydantic_schema_validation(self):
        """Verify that LeaseRules Pydantic model correctly validates structured data and cleans numbers."""
        sample_dict = {
            "base_rent": "$120,000",
            "base_rent_evidence": "ABC Retail Lease has a base annual rent of $120,000.",
            "rent_frequency": "annual",
            "cam_cap": "$10,000 per year",
            "cam_cap_evidence": "CAM expenses are capped at $10,000 per year.",
            "tenant_share": "15%",
            "tenant_share_evidence": "The tenant is responsible for 15% of applicable CAM expenses.",
            "administrative_fee_rules": "5% of CAM expenses",
            "administrative_fee_evidence": "Administrative fees may not exceed 5% of CAM expenses.",
            "audit_rights": "annual CAM reconciliation",
            "audit_rights_evidence": "The landlord must provide an annual CAM reconciliation."
        }

        rules = LeaseRules.model_validate(sample_dict)

        self.assertEqual(rules.base_rent, 120000.0)
        self.assertEqual(rules.rent_frequency, "annual")
        self.assertEqual(rules.cam_cap, 10000.0)
        self.assertEqual(rules.tenant_share, "15%")
        self.assertIn("5% of CAM", rules.administrative_fee_rules)
        self.assertIn("annual CAM reconciliation", rules.audit_rights)

    def test_empty_input_handling(self):
        """Verify that passing empty lease text returns a clean error payload without throwing an exception."""
        result = extract_lease_rules("")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["provider"], "none")
        self.assertIn("empty", result["message"].lower())

    @patch("services.ai._run_rocketride_extraction", new_callable=AsyncMock)
    def test_gemini_primary_success(self, mock_extraction):
        """Verify primary Gemini pipeline execution when Gemini succeeds."""
        mock_raw_json = {
            "base_rent": 120000.0,
            "base_rent_evidence": "base annual rent of $120,000",
            "rent_frequency": "annual",
            "cam_cap": 10000.0,
            "cam_cap_evidence": "CAM expenses are capped at $10,000 per year",
            "tenant_share": "15%",
            "tenant_share_evidence": "tenant is responsible for 15%",
            "administrative_fee_rules": "5% of CAM expenses",
            "audit_rights": "annual CAM reconciliation"
        }
        mock_extraction.return_value = mock_raw_json

        result = extract_lease_rules(SAMPLE_LEASE_TEXT)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(result["data"]["base_rent"], 120000.0)
        self.assertEqual(result["data"]["cam_cap"], 10000.0)

    @patch("services.ai._run_rocketride_extraction", new_callable=AsyncMock)
    def test_groq_fallback_when_gemini_fails(self, mock_extraction):
        """
        Verify that when Gemini pipeline fails (simulated exception),
        the system seamlessly falls back to Groq and returns provider='groq'.
        """
        mock_groq_json = {
            "base_rent": 120000.0,
            "base_rent_evidence": "base annual rent of $120,000",
            "rent_frequency": "annual",
            "cam_cap": 10000.0,
            "tenant_share": "15%",
            "administrative_fee_rules": "5% of CAM expenses",
            "audit_rights": "annual CAM reconciliation"
        }

        # First call (Gemini) raises RuntimeError; Second call (Groq) succeeds
        mock_extraction.side_effect = [
            RuntimeError("Gemini API rate limit / quota error"),
            mock_groq_json
        ]

        result = extract_lease_rules(SAMPLE_LEASE_TEXT)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "groq")
        self.assertTrue(result.get("fallback_used"))
        self.assertIn("Gemini API rate limit", result.get("primary_error", ""))
        self.assertEqual(result["data"]["base_rent"], 120000.0)

    @patch("services.ai._run_rocketride_extraction", new_callable=AsyncMock)
    def test_both_providers_failing(self, mock_extraction):
        """Verify that when both Gemini and Groq fail, a clear error payload is returned."""
        mock_extraction.side_effect = [
            RuntimeError("Gemini unavailable"),
            RuntimeError("Groq service timeout")
        ]

        result = extract_lease_rules(SAMPLE_LEASE_TEXT)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["provider"], "none")
        self.assertIn("Both Gemini and Groq AI providers failed", result["message"])


if __name__ == "__main__":
    unittest.main()
