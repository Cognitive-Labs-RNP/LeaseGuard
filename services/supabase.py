"""Supabase database client service for LeaseGuard AI."""

from __future__ import annotations

import datetime
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from services.auth import require_authenticated_user_id

load_dotenv()


class SupabaseService:
    """Service wrapper for interacting with Supabase PostgreSQL and Storage."""

    def __init__(self):
        self.url = (os.getenv("SUPABASE_URL") or "").strip()
        self.key = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()
        self.client: Optional[Client] = None

        if self.url and self.key and "your-project" not in self.url:
            try:
                self.client = create_client(self.url, self.key)
            except Exception:
                self.client = None

    def is_configured(self) -> bool:
        """Check if Supabase credentials are configured."""
        return bool(self.client is not None)

    def get_current_user_id(self) -> Optional[str]:
        """Return authenticated user ID or None if offline."""
        try:
            return require_authenticated_user_id()
        except Exception:
            return None

    def get_properties(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch properties belonging to current user."""
        active_user_id = user_id or self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        response = self.client.table("properties").select("*").eq("user_id", active_user_id).execute()
        return response.data or []

    def create_property(self, property_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create property and associate with user."""
        active_user_id = user_id or self.get_current_user_id()
        if self.client is None or not active_user_id:
            return property_data

        payload = dict(property_data)
        payload["user_id"] = active_user_id
        response = self.client.table("properties").insert(payload).execute()
        return (response.data or [property_data])[0]

    def get_documents(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch documents for current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        query = self.client.table("documents").select("*").eq("user_id", active_user_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def save_document(self, doc_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save document metadata to Supabase database."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "property_id": doc_data.get("property_id"),
            "document_type": doc_data.get("document_type") or doc_data.get("Type", "Lease Agreement"),
            "filename": doc_data.get("filename") or doc_data.get("Title", "Document.pdf"),
            "file_size": doc_data.get("file_size") or doc_data.get("File Size", "0 KB"),
            "storage_path": doc_data.get("storage_path") or doc_data.get("Title", "local"),
            "content_text": doc_data.get("content_text", ""),
            "status": doc_data.get("status") or doc_data.get("Status", "Uploaded & Indexed"),
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.client is not None and active_user_id:
            response = self.client.table("documents").insert(payload).execute()
            return (response.data or [payload])[0]

        return payload

    def get_audits(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch audits for current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        query = self.client.table("audits").select("*").eq("user_id", active_user_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def save_audit(self, audit_result: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save audit record to Supabase database."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "property_id": audit_result.get("property_id"),
            "audit_type": "lease_invoice_reconciliation",
            "title": f"Audit Session {now_iso[:10]}",
            "status": audit_result.get("status", "completed"),
            "summary": audit_result.get("summary", ""),
            "created_at": audit_result.get("timestamp", now_iso),
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.client is not None and active_user_id:
            response = self.client.table("audits").insert(payload).execute()
            saved = (response.data or [payload])[0]
            audit_id = saved.get("id")
            if audit_id and audit_result.get("findings"):
                self.save_findings(audit_result["findings"], audit_id, payload["property_id"], active_user_id)
            return saved

        return payload

    def get_findings(self, audit_id: Optional[str] = None, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch findings for current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        query = self.client.table("findings").select("*").eq("user_id", active_user_id)
        if audit_id:
            query = query.eq("audit_id", audit_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def save_findings(
        self,
        findings: List[Dict[str, Any]],
        audit_id: str,
        property_id: str,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Save structured audit discrepancy findings to Supabase database."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payloads = []
        for finding in findings:
            item = {
                "property_id": property_id,
                "audit_id": audit_id,
                "finding_type": finding.get("category", "Discrepancy"),
                "title": finding.get("category", "Discrepancy"),
                "description": finding.get("explanation", ""),
                "amount": finding.get("potential_recovery", 0.0),
                "severity": finding.get("severity", "medium"),
                "status": "open",
                "created_at": now_iso,
                "updated_at": now_iso,
            }
            if active_user_id:
                item["user_id"] = active_user_id
            payloads.append(item)

        if self.client is not None and active_user_id and payloads:
            response = self.client.table("findings").insert(payloads).execute()
            return response.data or payloads

        return payloads

    def save_risk_score(
        self,
        risk_result: Dict[str, Any],
        property_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save calculated risk score and factor analysis to Supabase database."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "property_id": property_id,
            "score": risk_result.get("overall_score") or risk_result.get("risk_score", 0.0),
            "risk_level": risk_result.get("risk_level", "Unassessed"),
            "summary": risk_result.get("summary", ""),
            "score_at": risk_result.get("timestamp", now_iso),
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.client is not None and active_user_id:
            response = self.client.table("risk_scores").insert(payload).execute()
            return (response.data or [payload])[0]

        return payload

    def get_risk_scores(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch risk scores for current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        query = self.client.table("risk_scores").select("*").eq("user_id", active_user_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def save_recovery_record(
        self,
        recovery_record: Dict[str, Any],
        property_id: str,
        audit_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save recovery tracking record to Supabase database."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "property_id": property_id,
            "audit_id": audit_id or recovery_record.get("audit_id"),
            "claim_amount": recovery_record.get("claim_amount") or recovery_record.get("potential_recovery", 0.0),
            "recovered_amount": recovery_record.get("recovered_amount", 0.0),
            "status": recovery_record.get("status", "Detected"),
            "notes": recovery_record.get("notes", ""),
            "created_at": recovery_record.get("created_at", now_iso),
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.client is not None and active_user_id:
            response = self.client.table("recovery_records").insert(payload).execute()
            return (response.data or [payload])[0]

        return payload

    def get_recovery_records(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch recovery records for current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        query = self.client.table("recovery_records").select("*").eq("user_id", active_user_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def update_recovery_status(
        self,
        record_id: str,
        new_status: str,
        recovered_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Update recovery record status and recovered amount in Supabase database."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload: Dict[str, Any] = {
            "status": new_status,
            "updated_at": now_iso,
        }
        if recovered_amount is not None:
            payload["recovered_amount"] = round(float(recovered_amount), 2)

        if self.client is not None:
            response = (
                self.client.table("recovery_records")
                .update(payload)
                .eq("id", record_id)
                .execute()
            )
            return (response.data or [payload])[0]

        payload["id"] = record_id
        return payload
