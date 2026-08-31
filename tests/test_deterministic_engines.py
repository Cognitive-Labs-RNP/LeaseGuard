"""
Unit Tests for Phase 4 Deterministic Engines (Audit Engine, Risk Engine, Recovery Engine).
"""

import unittest
from services.audit_engine import AuditEngine
from services.risk_engine import RiskEngine
from services.recovery_engine import RecoveryEngine, VALID_RECOVERY_STATUSES


class TestDeterministicEngines(unittest.TestCase):
    """Test suite for deterministic Phase 4 business logic components."""

    def setUp(self):
        self.audit_engine = AuditEngine()
        self.risk_engine = RiskEngine()
        self.recovery_engine = RecoveryEngine()

    # =========================================================================
    # Audit Engine Tests
    # =========================================================================

    def test_cam_overcharge(self):
        """Test CAM cap check generating a structured finding when billed CAM exceeds cap."""
        lease_data = {
            "cam_cap": 10000.0,
            "cam_cap_evidence": "Annual CAM expenses are capped at $10,000 per year."
        }
        invoice_data = {
            "billed_cam_amount": 14500.0,
            "cam_evidence": "Total billed CAM expenses: $14,500."
        }

        result = self.audit_engine.run_audit(lease_data, invoice_data, property_id="prop-001")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["findings_count"], 1)
        self.assertEqual(result["total_potential_recovery"], 4500.0)

        finding = result["findings"][0]
        self.assertEqual(finding["category"], "CAM Cap Exceeded")
        self.assertEqual(finding["billed_amount"], 14500.0)
        self.assertEqual(finding["allowed_amount"], 10000.0)
        self.assertEqual(finding["potential_recovery"], 4500.0)
        self.assertIn("exceeds the contractual lease cap", finding["explanation"])
        self.assertEqual(finding["lease_evidence"], lease_data["cam_cap_evidence"])

    def test_allowed_cam(self):
        """Test CAM cap check returning zero findings when billed CAM is within allowed cap."""
        lease_data = {
            "cam_cap": 15000.0
        }
        invoice_data = {
            "billed_cam_amount": 12000.0
        }

        result = self.audit_engine.run_audit(lease_data, invoice_data)

        self.assertEqual(result["findings_count"], 0)
        self.assertEqual(result["total_potential_recovery"], 0.0)

    def test_excluded_expense(self):
        """Test excluded expense check flagging prohibited billed line items."""
        lease_data = {
            "expense_exclusions": ["capital repairs", "legal fees"],
            "expense_exclusions_evidence": "Capital repairs and landlord legal fees excluded from CAM."
        }
        invoice_data = {
            "line_items": [
                {
                    "category": "Maintenance",
                    "description": "Routine janitorial service",
                    "billed_amount": 1200.0
                },
                {
                    "category": "Capital Improvements",
                    "description": "HVAC Unit Capital Repairs",
                    "billed_amount": 3500.0,
                    "evidence": "Billed HVAC replacement line item: $3,500"
                }
            ]
        }

        result = self.audit_engine.run_audit(lease_data, invoice_data)

        self.assertEqual(result["findings_count"], 1)
        finding = result["findings"][0]
        self.assertEqual(finding["category"], "Excluded Expense Billed")
        self.assertEqual(finding["billed_amount"], 3500.0)
        self.assertEqual(finding["allowed_amount"], 0.0)
        self.assertEqual(finding["potential_recovery"], 3500.0)

    def test_rent_escalation(self):
        """Test rent escalation check flagging billed rent exceeding allowed cap percentage."""
        lease_data = {
            "rent_escalation_cap_percent": 3.0,
            "rent_escalation_evidence": "Annual rent escalation capped at 3%."
        }
        invoice_data = {
            "prior_base_rent": 10000.0,
            "billed_base_rent": 10800.0
        }

        result = self.audit_engine.run_audit(lease_data, invoice_data)

        self.assertEqual(result["findings_count"], 1)
        finding = result["findings"][0]
        self.assertEqual(finding["category"], "Rent Escalation Overcharge")
        self.assertEqual(finding["billed_amount"], 10800.0)
        self.assertEqual(finding["allowed_amount"], 10300.0)
        self.assertEqual(finding["potential_recovery"], 500.0)

    def test_tenant_share_calculation(self):
        """Test tenant share calculation check flagging pro-rata share calculation errors."""
        lease_data = {
            "tenant_share": 15.0,
            "tenant_share_evidence": "Tenant share is 15%."
        }
        invoice_data = {
            "total_building_cam": 100000.0,
            "billed_tenant_share_amount": 18000.0
        }

        result = self.audit_engine.run_audit(lease_data, invoice_data)

        self.assertEqual(result["findings_count"], 1)
        finding = result["findings"][0]
        self.assertEqual(finding["category"], "Tenant Share Calculation Error")
        self.assertEqual(finding["billed_amount"], 18000.0)
        self.assertEqual(finding["allowed_amount"], 15000.0)
        self.assertEqual(finding["potential_recovery"], 3000.0)

    # =========================================================================
    # Recovery Engine Tests
    # =========================================================================

    def test_recovery_calculation(self):
        """Test recovery metrics calculation across all supported claim statuses."""
        records = [
            {"claim_amount": 5000.0, "recovered_amount": 0.0, "status": "Detected"},
            {"claim_amount": 3000.0, "recovered_amount": 0.0, "status": "Draft"},
            {"claim_amount": 4000.0, "recovered_amount": 0.0, "status": "Submitted"},
            {"claim_amount": 2500.0, "recovered_amount": 0.0, "status": "Under Review"},
            {"claim_amount": 6000.0, "recovered_amount": 6000.0, "status": "Recovered"},
            {"claim_amount": 1000.0, "recovered_amount": 0.0, "status": "Rejected"},
        ]

        metrics = self.recovery_engine.calculate_recovery_metrics(records)

        # Potential recovery excludes 'Rejected' (5000 + 3000 + 4000 + 2500 + 6000 = 20500)
        self.assertEqual(metrics["potential_recovery"], 20500.0)

        # Disputed amount includes Draft (3000) + Submitted (4000) + Under Review (2500) = 9500
        self.assertEqual(metrics["disputed_amount"], 9500.0)

        # Amount under review = 2500
        self.assertEqual(metrics["amount_under_review"], 2500.0)

        # Recovered amount = 6000
        self.assertEqual(metrics["recovered_amount"], 6000.0)

    def test_recovery_status_lifecycle(self):
        """Test status transitions and record creation in RecoveryEngine."""
        record = self.recovery_engine.create_recovery_record(
            property_id="prop-123",
            claim_amount=4500.0,
            status="Detected"
        )
        self.assertEqual(record["status"], "Detected")
        self.assertEqual(record["claim_amount"], 4500.0)

        # Transition to Draft
        updated = self.recovery_engine.update_recovery_status(record, "Draft")
        self.assertEqual(updated["status"], "Draft")

        # Transition to Recovered
        recovered_rec = self.recovery_engine.update_recovery_status(updated, "Recovered", recovered_amount=4500.0)
        self.assertEqual(recovered_rec["status"], "Recovered")
        self.assertEqual(recovered_rec["recovered_amount"], 4500.0)

        # Verify invalid status raises ValueError
        with self.assertRaises(ValueError):
            self.recovery_engine.update_recovery_status(record, "InvalidStatus")

    # =========================================================================
    # Risk Engine Tests
    # =========================================================================

    def test_risk_score(self):
        """Test risk score calculation, risk level assignment, and contributing factors."""
        # Uncapped lease data -> High Risk
        high_risk_lease = {
            "cam_rules": "Operating expenses billed as incurred",
            "rent_escalation_rules": "Market rate escalation",
            "administrative_fee_rules": "Management fees included",
            "audit_rights": "30 days notice"
        }
        high_findings = [{"category": "CAM Cap Exceeded", "potential_recovery": 5000.0}]

        result_high = self.risk_engine.calculate_lease_risk(high_risk_lease, high_findings)

        self.assertGreaterEqual(result_high["overall_score"], 70.0)
        self.assertEqual(result_high["risk_level"], "High Risk")
        self.assertIn("cam_risk", result_high["category_scores"])
        self.assertGreater(len(result_high["contributing_factors"]), 0)

        # Capped lease data -> Low/Moderate Risk
        low_risk_lease = {
            "cam_cap": 10000.0,
            "rent_escalation_cap_percent": 3.0,
            "administrative_fee_cap_percent": 5.0,
            "tax_responsibility": "Pro-rata tax share with protest rights",
            "audit_rights": "Annual audit rights window 365 days"
        }
        result_low = self.risk_engine.calculate_lease_risk(low_risk_lease)

        self.assertLess(result_low["overall_score"], 50.0)
        self.assertIn(result_low["risk_level"], ["Low Risk", "Moderate Risk"])


if __name__ == "__main__":
    unittest.main()
