"""Demo dataset for LeaseGuard AI.

These records are explicitly labeled as demonstration-only and should never be
presented as live tenant audit results. They let the app run and be showcased
without external integrations.
"""

from __future__ import annotations

from typing import Any, Dict, List

DEMO_PROPERTY = {
    "id": "demo-prop-001",
    "name": "Skyline Commercial Center",
    "code": "PROP-001",
    "address": "100 Financial Plaza, Suite 400",
    "square_feet": 25000,
    "status": "Active",
}

DEMO_LEASE_TEXT = """
Skyline Commercial Center Lease Agreement
Base rent: $120,000 per year.
CAM expenses are capped at $10,000 annually.
The tenant is responsible for 15% of total CAM expenses.
Administrative fees may not exceed 5% of CAM expenses.
Capital improvements and legal fees are excluded from operating expenses.
The landlord must provide annual CAM reconciliation.
"""

DEMO_INVOICE_TEXT = """
CAM Reconciliation Statement
Total billed CAM: $14,500.00.
Tenant share calculation: 15% of $100,000 = $15,000.
Administrative fee billed: $900.00.
Line items:
- Capital Improvements: Rooftop HVAC repair - $4,200.00
- Janitorial Services - $1,200.00
- General Maintenance - $2,400.00
"""

DEMO_LEASE_RULES = {
    "base_rent": 120000.0,
    "base_rent_evidence": "Base rent: $120,000 per year.",
    "rent_frequency": "annual",
    "cam_cap": 10000.0,
    "cam_cap_evidence": "CAM expenses are capped at $10,000 annually.",
    "tenant_share": "15%",
    "tenant_share_evidence": "The tenant is responsible for 15% of total CAM expenses.",
    "administrative_fee_rules": "5% of CAM expenses",
    "administrative_fee_evidence": "Administrative fees may not exceed 5% of CAM expenses.",
    "expense_exclusions": ["capital improvements", "legal fees"],
    "expense_exclusions_evidence": "Capital improvements and legal fees are excluded from operating expenses.",
    "audit_rights": "annual CAM reconciliation",
    "audit_rights_evidence": "The landlord must provide annual CAM reconciliation.",
    "relevant_lease_clauses": [
        "CAM expenses are capped at $10,000 annually.",
        "Administrative fees may not exceed 5% of CAM expenses.",
        "Capital improvements and legal fees are excluded from operating expenses.",
    ],
}

DEMO_FINDINGS = [
    {
        "id": "demo-finding-001",
        "property_id": DEMO_PROPERTY["id"],
        "audit_id": "demo-audit-001",
        "title": "CAM Cap Exceeded",
        "finding_type": "CAM Cap Exceeded",
        "category": "CAM Cap Exceeded",
        "description": "Demo finding: billed CAM exceeds the lease cap and was flagged for review.",
        "amount": 4500.0,
        "potential_recovery": 4500.0,
        "billed_amount": 14500.0,
        "allowed_amount": 10000.0,
        "severity": "high",
        "status": "open",
        "lease_evidence": DEMO_LEASE_RULES["cam_cap_evidence"],
        "invoice_evidence": "CAM Reconciliation Statement lists billed CAM of $14,500.00.",
        "created_at": "2026-08-31T00:00:00+00:00",
    },
    {
        "id": "demo-finding-002",
        "property_id": DEMO_PROPERTY["id"],
        "audit_id": "demo-audit-001",
        "title": "Excluded Expense Billed",
        "finding_type": "Excluded Expense Billed",
        "category": "Excluded Expense Billed",
        "description": "Demo finding: a capital improvement line item is not permitted under the lease.",
        "amount": 4200.0,
        "potential_recovery": 4200.0,
        "billed_amount": 4200.0,
        "allowed_amount": 0.0,
        "severity": "high",
        "status": "open",
        "lease_evidence": DEMO_LEASE_RULES["expense_exclusions_evidence"],
        "invoice_evidence": "Rooftop HVAC repair line item: $4,200.00.",
        "created_at": "2026-08-31T00:00:00+00:00",
    },
]

DEMO_RISK_SCORE = {
    "id": "demo-risk-001",
    "property_id": DEMO_PROPERTY["id"],
    "score": 72.5,
    "risk_level": "High Risk",
    "summary": "Demo assessment: lease terms are exposed to CAM and audit-right risk.",
    "overall_score": 72.5,
    "category_scores": {
        "cam_risk": 85.0,
        "rent_escalation_risk": 20.0,
        "administrative_fee_risk": 60.0,
        "tax_risk": 15.0,
        "audit_rights_risk": 80.0,
    },
    "contributing_factors": [
        "CAM Risk: Discrepancy flagged for CAM cap overcharge.",
        "Audit-Rights Risk: No explicit audit rights clause found.",
    ],
    "created_at": "2026-08-31T00:00:00+00:00",
}

DEMO_AUDIT = {
    "id": "demo-audit-001",
    "property_id": DEMO_PROPERTY["id"],
    "status": "completed",
    "summary": "Demo audit flagged 2 discrepancies with $8,700 in potential recovery.",
    "timestamp": "2026-08-31T00:00:00+00:00",
    "findings_count": 2,
    "total_potential_recovery": 8700.0,
    "total_billed": 18700.0,
    "total_allowed": 10000.0,
    "findings": DEMO_FINDINGS,
}

DEMO_RECOVERY_RECORDS = [
    {
        "id": "demo-recovery-001",
        "property_id": DEMO_PROPERTY["id"],
        "audit_id": "demo-audit-001",
        "claim_amount": 8700.0,
        "recovered_amount": 0.0,
        "status": "Detected",
        "notes": "Demo recovery record created for reconciliation review.",
        "created_at": "2026-08-31T00:00:00+00:00",
        "updated_at": "2026-08-31T00:00:00+00:00",
    }
]

DEMO_DOCUMENTS = [
    {
        "id": "demo-doc-lease",
        "property_id": DEMO_PROPERTY["id"],
        "document_type": "Lease Agreement",
        "filename": "demo_lease.pdf",
        "file_size": "1.2 MB",
        "storage_path": "demo/demo_lease.pdf",
        "content_text": DEMO_LEASE_TEXT,
        "status": "Uploaded & Indexed",
        "created_at": "2026-08-31T00:00:00+00:00",
        "Title": "demo_lease.pdf",
        "Type": "Lease Agreement",
        "Property": DEMO_PROPERTY["name"],
        "File Size": "1.2 MB",
        "Status": "Uploaded & Indexed",
    },
    {
        "id": "demo-doc-invoice",
        "property_id": DEMO_PROPERTY["id"],
        "document_type": "CAM Reconciliation Statement",
        "filename": "demo_invoice.pdf",
        "file_size": "0.8 MB",
        "storage_path": "demo/demo_invoice.pdf",
        "content_text": DEMO_INVOICE_TEXT,
        "status": "Uploaded & Indexed",
        "created_at": "2026-08-31T00:00:00+00:00",
        "Title": "demo_invoice.pdf",
        "Type": "CAM Reconciliation Statement",
        "Property": DEMO_PROPERTY["name"],
        "File Size": "0.8 MB",
        "Status": "Uploaded & Indexed",
    },
]


def is_demo_mode() -> bool:
    """Return True when the app has been explicitly switched into demo mode."""
    import os

    value = (os.getenv("DEMO_MODE") or "").strip().lower()
    return value in {"1", "true", "yes", "on", "demo"} or (os.getenv("APP_ENV") or "").strip().lower() == "demo"


def get_demo_app_records() -> Dict[str, List[Dict[str, Any]]]:
    """Return all demo records used for showcase mode."""
    return {
        "properties": [DEMO_PROPERTY],
        "documents": DEMO_DOCUMENTS,
        "audits": [DEMO_AUDIT],
        "findings": DEMO_FINDINGS,
        "risk_scores": [DEMO_RISK_SCORE],
        "recovery_records": DEMO_RECOVERY_RECORDS,
    }
