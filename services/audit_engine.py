"""
Audit Engine Service (Phase 4).
Performs deterministic rule reconciliation between lease obligations and invoice charges.
Strictly calculates mathematical values in Python without relying on AI for numbers.
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Dict, List, Optional


def _parse_float(val: Any) -> Optional[float]:
    """Helper to cleanly convert numeric values or currency strings to float."""
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


class AuditEngine:
    """Deterministic business logic engine for commercial lease auditing."""

    def __init__(self):
        pass

    def run_audit(
        self,
        lease_data: Dict[str, Any],
        invoice_data: Dict[str, Any],
        property_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute deterministic reconciliation between lease rules and invoice line items.

        Args:
            lease_data: Extracted lease rules dictionary.
            invoice_data: Billed invoice line items and totals dictionary.
            property_id: Optional associated property UUID.

        Returns:
            Dict containing audit session metadata, summary totals, and structured findings.
        """
        findings: List[Dict[str, Any]] = []

        # 1. CAM Cap Check
        cam_finding = self._check_cam_cap(lease_data, invoice_data)
        if cam_finding:
            findings.append(cam_finding)

        # Calculate allowable CAM baseline for Admin Fee check
        allowable_cam = self._get_allowable_cam(lease_data, invoice_data)

        # 2. Administrative Fee Check
        admin_finding = self._check_administrative_fee(lease_data, invoice_data, allowable_cam)
        if admin_finding:
            findings.append(admin_finding)

        # 3. Excluded Expense Check
        exclusion_findings = self._check_excluded_expenses(lease_data, invoice_data)
        findings.extend(exclusion_findings)

        # 4. Rent Escalation Check
        escalation_finding = self._check_rent_escalation(lease_data, invoice_data)
        if escalation_finding:
            findings.append(escalation_finding)

        # 5. Tenant Share Calculation Check
        tenant_share_finding = self._check_tenant_share(lease_data, invoice_data)
        if tenant_share_finding:
            findings.append(tenant_share_finding)

        # Aggregate totals
        total_billed = sum(f["billed_amount"] for f in findings)
        total_allowed = sum(f["allowed_amount"] for f in findings)
        total_potential_recovery = sum(f["potential_recovery"] for f in findings)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "property_id": property_id,
            "status": "completed",
            "timestamp": timestamp,
            "findings_count": len(findings),
            "total_billed": round(total_billed, 2),
            "total_allowed": round(total_allowed, 2),
            "total_potential_recovery": round(total_potential_recovery, 2),
            "findings": findings,
            "summary": (
                f"Audit flagged {len(findings)} discrepancy(ies) with total potential "
                f"recovery of ${total_potential_recovery:,.2f}."
            )
        }

    def _get_allowable_cam(self, lease_data: Dict[str, Any], invoice_data: Dict[str, Any]) -> float:
        """Determine allowable CAM amount for administrative fee benchmarking."""
        billed_cam = _parse_float(invoice_data.get("billed_cam_amount")) or 0.0
        cam_cap = _parse_float(lease_data.get("cam_cap"))
        if cam_cap is not None and billed_cam > cam_cap:
            return cam_cap
        return billed_cam

    def _check_cam_cap(
        self, lease_data: Dict[str, Any], invoice_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Verify if billed CAM expenses exceed contractual cap."""
        cam_cap = _parse_float(lease_data.get("cam_cap"))
        billed_cam = _parse_float(invoice_data.get("billed_cam_amount"))

        if cam_cap is None or billed_cam is None:
            return None

        if billed_cam > cam_cap:
            recovery = billed_cam - cam_cap
            lease_ev = (
                lease_data.get("cam_cap_evidence")
                or f"Contractual annual CAM expense cap is ${cam_cap:,.2f}."
            )
            invoice_ev = (
                invoice_data.get("cam_evidence")
                or f"Billed total CAM amount is ${billed_cam:,.2f}."
            )
            return {
                "category": "CAM Cap Exceeded",
                "severity": "high" if recovery > 5000.0 else "medium",
                "billed_amount": round(billed_cam, 2),
                "allowed_amount": round(cam_cap, 2),
                "potential_recovery": round(recovery, 2),
                "explanation": (
                    f"Billed CAM amount (${billed_cam:,.2f}) exceeds the contractual "
                    f"lease cap of ${cam_cap:,.2f} by ${recovery:,.2f}."
                ),
                "lease_evidence": lease_ev,
                "invoice_evidence": invoice_ev,
            }
        return None

    def _check_administrative_fee(
        self, lease_data: Dict[str, Any], invoice_data: Dict[str, Any], allowable_cam: float
    ) -> Optional[Dict[str, Any]]:
        """Verify if billed administrative/management fees exceed contractual limit."""
        admin_cap_pct = _parse_float(
            lease_data.get("administrative_fee_cap_percent")
            or lease_data.get("administrative_fee_rules")
        )
        billed_admin = _parse_float(
            invoice_data.get("billed_admin_fee_amount")
            or invoice_data.get("administrative_fee_billed")
        )

        if admin_cap_pct is None or billed_admin is None:
            return None

        allowed_admin = allowable_cam * (admin_cap_pct / 100.0)

        if billed_admin > allowed_admin:
            recovery = billed_admin - allowed_admin
            lease_ev = (
                lease_data.get("administrative_fee_evidence")
                or f"Administrative fee capped at {admin_cap_pct}% of allowable CAM expenses."
            )
            invoice_ev = (
                invoice_data.get("admin_fee_evidence")
                or f"Billed administrative fee amount: ${billed_admin:,.2f}."
            )
            return {
                "category": "Administrative Fee Overcharge",
                "severity": "medium",
                "billed_amount": round(billed_admin, 2),
                "allowed_amount": round(allowed_admin, 2),
                "potential_recovery": round(recovery, 2),
                "explanation": (
                    f"Billed administrative fee (${billed_admin:,.2f}) exceeds the contractual "
                    f"limit of {admin_cap_pct}% (${allowed_admin:,.2f}) by ${recovery:,.2f}."
                ),
                "lease_evidence": lease_ev,
                "invoice_evidence": invoice_ev,
            }
        return None

    def _check_excluded_expenses(
        self, lease_data: Dict[str, Any], invoice_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify line items matching explicit lease expense exclusions."""
        findings = []
        raw_exclusions = lease_data.get("expense_exclusions") or []
        if isinstance(raw_exclusions, str):
            exclusions = [e.strip().lower() for e in raw_exclusions.split(",") if e.strip()]
        elif isinstance(raw_exclusions, list):
            exclusions = [str(e).strip().lower() for e in raw_exclusions if str(e).strip()]
        else:
            exclusions = []

        if not exclusions:
            return findings

        line_items = invoice_data.get("line_items") or []
        lease_ev = (
            lease_data.get("expense_exclusions_evidence")
            or f"Explicit lease exclusions: {', '.join(exclusions)}"
        )

        for item in line_items:
            category = str(item.get("category", "")).lower()
            desc = str(item.get("description", "")).lower()
            amount = _parse_float(item.get("billed_amount")) or 0.0

            if amount <= 0.0:
                continue

            matched_exclusion = None
            for excl in exclusions:
                if excl in category or excl in desc:
                    matched_exclusion = excl
                    break

            if matched_exclusion:
                item_desc = item.get("description") or item.get("category") or "Billed item"
                invoice_ev = item.get("evidence") or f"Invoice line item: {item_desc} (${amount:,.2f})"
                findings.append({
                    "category": "Excluded Expense Billed",
                    "severity": "high",
                    "billed_amount": round(amount, 2),
                    "allowed_amount": 0.0,
                    "potential_recovery": round(amount, 2),
                    "explanation": (
                        f"Invoice includes prohibited expense line item '{item_desc}' (${amount:,.2f}) "
                        f"matching lease exclusion '{matched_exclusion}'."
                    ),
                    "lease_evidence": lease_ev,
                    "invoice_evidence": invoice_ev,
                })

        return findings

    def _check_rent_escalation(
        self, lease_data: Dict[str, Any], invoice_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Verify if billed base rent exceeds contractual escalation cap."""
        escalation_cap_pct = _parse_float(
            lease_data.get("rent_escalation_cap_percent")
            or lease_data.get("rent_escalation_rules")
        )
        prior_base_rent = _parse_float(
            invoice_data.get("prior_base_rent")
            or lease_data.get("base_rent")
        )
        billed_base_rent = _parse_float(invoice_data.get("billed_base_rent"))

        if escalation_cap_pct is None or prior_base_rent is None or billed_base_rent is None:
            return None

        allowed_base_rent = prior_base_rent * (1.0 + escalation_cap_pct / 100.0)

        if billed_base_rent > allowed_base_rent:
            recovery = billed_base_rent - allowed_base_rent
            lease_ev = (
                lease_data.get("rent_escalation_evidence")
                or f"Base rent annual escalation capped at {escalation_cap_pct}%."
            )
            invoice_ev = (
                invoice_data.get("rent_evidence")
                or f"Billed base rent amount: ${billed_base_rent:,.2f}."
            )
            return {
                "category": "Rent Escalation Overcharge",
                "severity": "high",
                "billed_amount": round(billed_base_rent, 2),
                "allowed_amount": round(allowed_base_rent, 2),
                "potential_recovery": round(recovery, 2),
                "explanation": (
                    f"Billed base rent (${billed_base_rent:,.2f}) exceeds contractual "
                    f"maximum escalation limit of {escalation_cap_pct}% (${allowed_base_rent:,.2f}) by ${recovery:,.2f}."
                ),
                "lease_evidence": lease_ev,
                "invoice_evidence": invoice_ev,
            }
        return None

    def _check_tenant_share(
        self, lease_data: Dict[str, Any], invoice_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Verify if billed tenant CAM pro-rata share matches contractual percentage."""
        tenant_share_pct = _parse_float(lease_data.get("tenant_share"))
        total_building_cam = _parse_float(invoice_data.get("total_building_cam"))
        billed_tenant_cam = _parse_float(
            invoice_data.get("billed_tenant_share_amount")
            or invoice_data.get("billed_cam_amount")
        )

        if tenant_share_pct is None or total_building_cam is None or billed_tenant_cam is None:
            return None

        expected_tenant_cam = total_building_cam * (tenant_share_pct / 100.0)

        if billed_tenant_cam > expected_tenant_cam:
            recovery = billed_tenant_cam - expected_tenant_cam
            lease_ev = (
                lease_data.get("tenant_share_evidence")
                or f"Tenant pro-rata share is {tenant_share_pct}% of total building CAM."
            )
            invoice_ev = (
                invoice_data.get("tenant_share_evidence")
                or f"Billed tenant CAM share: ${billed_tenant_cam:,.2f} (Total CAM: ${total_building_cam:,.2f})."
            )
            return {
                "category": "Tenant Share Calculation Error",
                "severity": "medium",
                "billed_amount": round(billed_tenant_cam, 2),
                "allowed_amount": round(expected_tenant_cam, 2),
                "potential_recovery": round(recovery, 2),
                "explanation": (
                    f"Billed tenant CAM share (${billed_tenant_cam:,.2f}) exceeds contractual "
                    f"pro-rata share of {tenant_share_pct}% (${expected_tenant_cam:,.2f}) by ${recovery:,.2f}."
                ),
                "lease_evidence": lease_ev,
                "invoice_evidence": invoice_ev,
            }
        return None
