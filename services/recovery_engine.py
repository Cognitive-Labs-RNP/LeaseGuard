"""
Recovery Engine Service (Phase 4).
Tracks financial recovery metrics, overcharge claim lifecycles, and landlord settlement status.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

VALID_RECOVERY_STATUSES = {
    "Detected",
    "Draft",
    "Submitted",
    "Under Review",
    "Recovered",
    "Rejected",
}


class RecoveryEngine:
    """Computes recoverable amounts, claim tracking metrics, and workflow state transitions."""

    def __init__(self):
        pass

    def calculate_recovery_metrics(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregated financial metrics across recovery claims.

        Args:
            records: List of claim dictionaries or database rows.

        Returns:
            Dict containing potential recovery, disputed amount, amount under review, and recovered amount.
        """
        potential_recovery = 0.0
        disputed_amount = 0.0
        amount_under_review = 0.0
        recovered_amount = 0.0

        disputed_statuses = {"Draft", "Submitted", "Under Review"}

        for rec in records:
            status = rec.get("status", "Detected")
            claim = float(rec.get("claim_amount") or rec.get("potential_recovery") or 0.0)
            rec_amt = float(rec.get("recovered_amount") or 0.0)

            # Potential recovery includes all active non-rejected claims
            if status != "Rejected":
                potential_recovery += claim

            # Disputed amount includes Draft, Submitted, and Under Review
            if status in disputed_statuses:
                disputed_amount += claim

            # Amount specifically in Under Review
            if status == "Under Review":
                amount_under_review += claim

            # Recovered amount
            if status == "Recovered":
                recovered_amount += rec_amt if rec_amt > 0 else claim

        return {
            "potential_recovery": round(potential_recovery, 2),
            "disputed_amount": round(disputed_amount, 2),
            "amount_under_review": round(amount_under_review, 2),
            "recovered_amount": round(recovered_amount, 2),
            "total_claims_count": len(records),
            "status": "active"
        }

    def create_recovery_record(
        self,
        property_id: str,
        claim_amount: float,
        audit_id: Optional[str] = None,
        status: str = "Detected",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Construct a structured recovery record payload.

        Args:
            property_id: Target property UUID.
            claim_amount: Billed overcharge amount to claim.
            audit_id: Optional reference audit UUID.
            status: Initial lifecycle status (must be one of VALID_RECOVERY_STATUSES).
            notes: Optional contextual notes or description.
        """
        if status not in VALID_RECOVERY_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {sorted(list(VALID_RECOVERY_STATUSES))}"
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "property_id": property_id,
            "audit_id": audit_id,
            "claim_amount": round(float(claim_amount), 2),
            "recovered_amount": 0.0 if status != "Recovered" else round(float(claim_amount), 2),
            "status": status,
            "notes": notes or f"Claim created in status {status}",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

    def update_recovery_status(
        self,
        record: Dict[str, Any],
        new_status: str,
        recovered_amount: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update status and recovered amount of an existing recovery claim.

        Args:
            record: Dictionary of existing record.
            new_status: Target status to transition to.
            recovered_amount: Optional explicit settled sum.
            notes: Optional transition notes.
        """
        if new_status not in VALID_RECOVERY_STATUSES:
            raise ValueError(
                f"Invalid status '{new_status}'. Must be one of {sorted(list(VALID_RECOVERY_STATUSES))}"
            )

        updated_record = dict(record)
        updated_record["status"] = new_status
        updated_record["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if recovered_amount is not None:
            updated_record["recovered_amount"] = round(float(recovered_amount), 2)
        elif new_status == "Recovered" and updated_record.get("recovered_amount", 0) <= 0:
            updated_record["recovered_amount"] = updated_record.get("claim_amount", 0.0)

        if notes:
            updated_record["notes"] = notes

        return updated_record
