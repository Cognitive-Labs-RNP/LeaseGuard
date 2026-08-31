"""
Risk Engine Service (Phase 4).
Calculates deterministic risk scores (0-100) for commercial leases and portfolio properties.
Uses explainable, multi-factor category scoring for audit vulnerability and exposure.
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Dict, List, Optional


def _parse_float(val: Any) -> Optional[float]:
    """Helper to convert numeric values or currency/percent strings to float."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        cleaned = re.sub(r"[^\d.]", "", val.replace(",", ""))
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                pass
    return None


class RiskEngine:
    """Calculates deterministic lease risk scores and financial exposure ratings."""

    def __init__(self):
        pass

    def calculate_lease_risk(
        self,
        lease_data: Dict[str, Any],
        findings: Optional[List[Dict[str, Any]]] = None,
        property_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate composite risk score (0-100) for a lease agreement.

        Args:
            lease_data: Extracted lease rules dictionary.
            findings: List of identified overcharge findings (optional).
            property_id: Associated property UUID (optional).

        Returns:
            Dict containing overall score, risk level, category scores, and contributing factors.
        """
        findings = findings or []
        contributing_factors: List[str] = []

        # 1. CAM Risk
        cam_score, cam_factors = self._evaluate_cam_risk(lease_data, findings)
        contributing_factors.extend(cam_factors)

        # 2. Rent Escalation Risk
        esc_score, esc_factors = self._evaluate_rent_escalation_risk(lease_data, findings)
        contributing_factors.extend(esc_factors)

        # 3. Administrative Fee Risk
        admin_score, admin_factors = self._evaluate_admin_fee_risk(lease_data, findings)
        contributing_factors.extend(admin_factors)

        # 4. Tax Risk
        tax_score, tax_factors = self._evaluate_tax_risk(lease_data, findings)
        contributing_factors.extend(tax_factors)

        # 5. Audit Rights Risk
        audit_score, audit_factors = self._evaluate_audit_rights_risk(lease_data, findings)
        contributing_factors.extend(audit_factors)

        category_scores = {
            "cam_risk": round(cam_score, 1),
            "rent_escalation_risk": round(esc_score, 1),
            "administrative_fee_risk": round(admin_score, 1),
            "tax_risk": round(tax_score, 1),
            "audit_rights_risk": round(audit_score, 1),
        }

        # Weighted composite score: CAM 30%, Rent Escalation 25%, Admin Fee 15%, Tax 15%, Audit Rights 15%
        overall_score = (
            cam_score * 0.30 +
            esc_score * 0.25 +
            admin_score * 0.15 +
            tax_score * 0.15 +
            audit_score * 0.15
        )
        overall_score = round(min(100.0, max(0.0, overall_score)), 1)

        if overall_score >= 70.0:
            risk_level = "High Risk"
        elif overall_score >= 30.0:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Low Risk"

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "property_id": property_id,
            "overall_score": overall_score,
            "risk_score": overall_score,  # Alias for DB integration
            "risk_level": risk_level,
            "category_scores": category_scores,
            "contributing_factors": contributing_factors,
            "summary": f"Lease assessed as {risk_level} with a score of {overall_score}/100.",
            "timestamp": timestamp
        }

    def _evaluate_cam_risk(
        self, lease_data: Dict[str, Any], findings: List[Dict[str, Any]]
    ) -> tuple[float, List[str]]:
        factors = []
        score = 0.0

        cam_cap = _parse_float(lease_data.get("cam_cap"))
        cam_rules = str(lease_data.get("cam_rules") or "").lower()

        if cam_cap is None and "capped" not in cam_rules and "cap" not in cam_rules:
            score += 70.0
            factors.append("CAM Risk: Uncapped CAM expenses in lease agreement.")
        elif cam_cap is not None:
            score += 15.0
            factors.append(f"CAM Risk: Explicit CAM cap present (${cam_cap:,.2f}).")
        else:
            score += 40.0
            factors.append("CAM Risk: Ambiguous or unquantified CAM expense terms.")

        has_cam_overcharge = any(f.get("category") == "CAM Cap Exceeded" for f in findings)
        if has_cam_overcharge:
            score += 30.0
            factors.append("CAM Risk: Discrepancy flagged for CAM cap overcharge.")

        return min(100.0, score), factors

    def _evaluate_rent_escalation_risk(
        self, lease_data: Dict[str, Any], findings: List[Dict[str, Any]]
    ) -> tuple[float, List[str]]:
        factors = []
        score = 0.0

        esc_pct = _parse_float(
            lease_data.get("rent_escalation_cap_percent")
            or lease_data.get("rent_escalation_rules")
        )
        esc_rules = str(lease_data.get("rent_escalation_rules") or "").lower()

        if esc_pct is None and "capped" not in esc_rules and "max" not in esc_rules:
            score += 60.0
            factors.append("Rent Escalation Risk: Uncapped rent escalation clause.")
        elif esc_pct is not None:
            if esc_pct > 5.0:
                score += 40.0
                factors.append(f"Rent Escalation Risk: High escalation cap ({esc_pct}%).")
            else:
                score += 10.0
                factors.append(f"Rent Escalation Risk: Standard escalation cap ({esc_pct}%).")
        else:
            score += 30.0
            factors.append("Rent Escalation Risk: Vague or unindexed escalation rules.")

        has_esc_overcharge = any(f.get("category") == "Rent Escalation Overcharge" for f in findings)
        if has_esc_overcharge:
            score += 40.0
            factors.append("Rent Escalation Risk: Discrepancy flagged for rent escalation overcharge.")

        return min(100.0, score), factors

    def _evaluate_admin_fee_risk(
        self, lease_data: Dict[str, Any], findings: List[Dict[str, Any]]
    ) -> tuple[float, List[str]]:
        factors = []
        score = 0.0

        admin_pct = _parse_float(
            lease_data.get("administrative_fee_cap_percent")
            or lease_data.get("administrative_fee_rules")
        )

        if admin_pct is None:
            score += 60.0
            factors.append("Administrative Fee Risk: Uncapped administrative/management fees.")
        elif admin_pct > 8.0:
            score += 45.0
            factors.append(f"Administrative Fee Risk: High administrative fee limit ({admin_pct}%).")
        else:
            score += 10.0
            factors.append(f"Administrative Fee Risk: Controlled administrative fee cap ({admin_pct}%).")

        has_admin_overcharge = any(f.get("category") == "Administrative Fee Overcharge" for f in findings)
        if has_admin_overcharge:
            score += 40.0
            factors.append("Administrative Fee Risk: Discrepancy flagged for admin fee overcharge.")

        return min(100.0, score), factors

    def _evaluate_tax_risk(
        self, lease_data: Dict[str, Any], findings: List[Dict[str, Any]]
    ) -> tuple[float, List[str]]:
        factors = []
        score = 0.0

        tax_resp = str(lease_data.get("tax_responsibility") or "").lower()

        if not tax_resp or tax_resp == "none":
            score += 60.0
            factors.append("Tax Risk: Unspecified real estate tax responsibility terms.")
        elif "protest" not in tax_resp and "appeal" not in tax_resp:
            score += 40.0
            factors.append("Tax Risk: Tax clause lacks tenant tax protest refund pass-through provisions.")
        else:
            score += 10.0
            factors.append("Tax Risk: Clear tax pass-through structure with protest rights.")

        return min(100.0, score), factors

    def _evaluate_audit_rights_risk(
        self, lease_data: Dict[str, Any], findings: List[Dict[str, Any]]
    ) -> tuple[float, List[str]]:
        factors = []
        score = 0.0

        audit_terms = str(lease_data.get("audit_rights") or "").lower()

        if not audit_terms or audit_terms == "none":
            score += 80.0
            factors.append("Audit-Rights Risk: No explicit audit rights clause found.")
        elif "30 days" in audit_terms or "60 days" in audit_terms:
            score += 65.0
            factors.append("Audit-Rights Risk: Restrictive audit notification window (< 90 days).")
        else:
            score += 10.0
            factors.append("Audit-Rights Risk: Standard annual audit rights clause present.")

        return min(100.0, score), factors
