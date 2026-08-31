"""Supabase database client service for LeaseGuard AI."""

from __future__ import annotations

import datetime
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from services.auth import require_authenticated_user_id
from services.demo_data import get_demo_app_records, is_demo_mode

load_dotenv()

logger = logging.getLogger("leaseguard.supabase")

# In-memory document text cache for extracted document text content
_DOCUMENT_TEXT_CACHE: Dict[str, str] = {}


class SupabaseService:
    """Service wrapper for interacting with Supabase PostgreSQL and Storage."""

    def __init__(self):
        self.url = (os.getenv("SUPABASE_URL") or "").strip()
        self.key = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()
        self.client: Optional[Client] = None
        self.demo_mode = is_demo_mode()

        if self.url and self.key and "your-project" not in self.url:
            try:
                self.client = create_client(self.url, self.key)

                # Check for active user session tokens in Streamlit session_state
                access_token = None
                refresh_token = None
                try:
                    import streamlit as st
                    access_token = st.session_state.get("access_token")
                    refresh_token = st.session_state.get("refresh_token")
                except Exception:
                    pass

                if access_token and self.client is not None:
                    # Authenticate PostgREST queries with user's Bearer token
                    self.client.postgrest.auth(access_token)
                    try:
                        self.client.auth.set_session(access_token, refresh_token or "")
                    except Exception:
                        pass
                    logger.debug("SupabaseService initialized with user session (access_token_present=True).")
            except Exception as exc:
                logger.warning("Supabase client initialization exception: %s", str(exc))
                self.client = None

    def is_configured(self) -> bool:
        """Check if Supabase credentials are configured."""
        return bool(self.client is not None)

    def get_current_user_id(self) -> Optional[str]:
        """Return authenticated user ID or None if unauthenticated."""
        try:
            import streamlit as st
            uid = st.session_state.get("user_id")
            if uid:
                return str(uid)
            auth_u = st.session_state.get("authenticated_user")
            if isinstance(auth_u, dict) and auth_u.get("id"):
                return str(auth_u.get("id"))
        except Exception:
            pass

        try:
            return require_authenticated_user_id()
        except Exception:
            return None

    def get_properties(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch properties belonging to current user."""
        if self.demo_mode:
            raw_props = list(get_demo_app_records()["properties"])
        else:
            active_user_id = user_id or self.get_current_user_id()
            if self.client is None or not active_user_id:
                return []
            try:
                response = self.client.table("properties").select("*").eq("user_id", active_user_id).execute()
                raw_props = response.data or []
            except Exception as exc:
                logger.warning("Supabase get_properties error: %s", str(exc))
                return []

        # Normalize returned records so both `code`/`property_code` and `square_feet`/`square_footage` exist
        normalized = []
        for item in raw_props:
            p = dict(item)
            p["code"] = p.get("property_code") or p.get("code") or "PROP-001"
            p["property_code"] = p["code"]
            p["square_feet"] = float(p.get("square_footage") or p.get("square_feet") or 0.0)
            p["square_footage"] = p["square_feet"]
            normalized.append(p)
        return normalized

    def create_property(self, property_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create property in Supabase public.properties table."""
        active_user_id = user_id or self.get_current_user_id()
        pcode = property_data.get("property_code") or property_data.get("code") or f"PROP-{datetime.datetime.now().strftime('%H%M%S')}"
        sqft = float(property_data.get("square_footage") or property_data.get("square_feet") or 0.0)

        if self.demo_mode:
            res = dict(property_data)
            res["id"] = f"demo-prop-{datetime.datetime.now().strftime('%M%S')}"
            res["code"] = pcode
            res["property_code"] = pcode
            res["square_feet"] = sqft
            res["square_footage"] = sqft
            return res

        if not active_user_id:
            raise RuntimeError("Database connection or authentication error. Please sign in.")

        if self.client is None:
            raise RuntimeError("Database connection not configured.")

        payload = {
            "user_id": active_user_id,
            "property_code": str(pcode),
            "name": str(property_data.get("name") or "New Property"),
            "address": str(property_data.get("address") or "N/A"),
            "city": property_data.get("city"),
            "state": property_data.get("state"),
            "zip_code": property_data.get("zip_code"),
            "square_footage": sqft,
            "status": str(property_data.get("status") or "Active"),
        }

        try:
            response = self.client.table("properties").insert(payload).execute()
            saved = (response.data or [payload])[0]
            saved["code"] = saved.get("property_code") or pcode
            saved["square_feet"] = saved.get("square_footage") or sqft
            return saved
        except Exception as exc:
            logger.warning("Supabase create_property error: %s", str(exc))
            err_str = str(exc)
            if "42501" in err_str or "row-level security" in err_str.lower():
                raise RuntimeError(
                    "Database insert blocked by Row-Level Security (RLS Code 42501). "
                    "Please open database/schema.sql and run it in your Supabase SQL Editor to enable RLS policies for authenticated users."
                ) from exc
            raise RuntimeError(f"Failed to save property to Supabase: {err_str}") from exc

    def get_documents(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch document metadata for current user."""
        if self.demo_mode:
            records = list(get_demo_app_records()["documents"])
            if property_id:
                records = [r for r in records if str(r.get("property_id")) == str(property_id)]
            raw_docs = records
        else:
            active_user_id = self.get_current_user_id()
            if self.client is None or not active_user_id:
                return []
            try:
                query = self.client.table("documents").select("*").eq("user_id", active_user_id)
                if property_id:
                    query = query.eq("property_id", property_id)
                response = query.execute()
                raw_docs = response.data or []
            except Exception as exc:
                logger.warning("Supabase get_documents error: %s", str(exc))
                return []

        normalized = []
        for d in raw_docs:
            item = dict(d)
            item["filename"] = item.get("file_name") or item.get("title") or item.get("filename") or "Document.pdf"
            item["title"] = item.get("title") or item["filename"]
            item["document_type"] = item.get("document_type") or item.get("Type") or "Lease Agreement"
            fname = item["filename"]
            item["content_text"] = _DOCUMENT_TEXT_CACHE.get(fname) or _DOCUMENT_TEXT_CACHE.get(f"{item.get('property_id')}_{item['document_type']}") or item.get("content_text", "")
            normalized.append(item)
        return normalized

    def save_document(self, doc_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save document metadata to Supabase database and cache extracted text."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        fname = doc_data.get("file_name") or doc_data.get("filename") or doc_data.get("Title") or "Document.pdf"
        d_type = doc_data.get("document_type") or doc_data.get("Type") or "Lease Agreement"
        prop_id = doc_data.get("property_id")

        # Parse file_size to integer bytes for SQL schema
        fsize_raw = doc_data.get("file_size") or doc_data.get("File Size") or 0
        if isinstance(fsize_raw, (int, float)):
            fsize_bytes = int(fsize_raw)
        else:
            try:
                clean_s = str(fsize_raw).replace("KB", "").replace("MB", "").replace("bytes", "").strip()
                val = float(clean_s)
                fsize_bytes = int(val * 1024 * 1024) if "MB" in str(fsize_raw) else int(val * 1024)
            except Exception:
                fsize_bytes = 1024

        text_content = doc_data.get("content_text") or ""
        if text_content:
            _DOCUMENT_TEXT_CACHE[fname] = text_content
            if prop_id:
                _DOCUMENT_TEXT_CACHE[f"{prop_id}_{d_type}"] = text_content
                _DOCUMENT_TEXT_CACHE[f"{prop_id}_{fname}"] = text_content

        payload = {
            "property_id": prop_id,
            "document_type": d_type,
            "title": fname,
            "file_name": fname,
            "storage_path": doc_data.get("storage_path") or f"documents/{fname}",
            "file_size": fsize_bytes,
            "status": doc_data.get("status") or doc_data.get("Status") or "Uploaded & Indexed",
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.demo_mode:
            saved = {**payload, "id": f"demo-doc-{len(get_demo_app_records()['documents']) + 1}", "content_text": text_content, "filename": fname}
            return saved

        if self.client is not None and active_user_id:
            try:
                response = self.client.table("documents").insert(payload).execute()
                saved = (response.data or [payload])[0]
                saved["content_text"] = text_content
                saved["filename"] = fname
                return saved
            except Exception as exc:
                logger.warning("Supabase save_document error: %s", str(exc))
                raise RuntimeError(f"Failed to save document to Supabase: {str(exc)}") from exc

        return {**payload, "content_text": text_content, "filename": fname}

    def get_audits(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch audits for current user."""
        if self.demo_mode:
            records = list(get_demo_app_records()["audits"])
            if property_id:
                return [r for r in records if str(r.get("property_id")) == str(property_id)]
            return records
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        try:
            query = self.client.table("audits").select("*").eq("user_id", active_user_id)
            if property_id:
                query = query.eq("property_id", property_id)
            response = query.execute()
            return response.data or []
        except Exception as exc:
            logger.warning("Supabase get_audits error: %s", str(exc))
            return []

    def save_audit(self, audit_result: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save audit record and discrepancy findings to Supabase database."""
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

        if self.demo_mode:
            saved = {**payload, "id": f"demo-audit-{datetime.datetime.now().strftime('%M%S')}"}
            if audit_result.get("findings"):
                self.save_findings(audit_result["findings"], saved["id"], payload["property_id"], active_user_id)
            return saved

        if self.client is not None and active_user_id:
            try:
                response = self.client.table("audits").insert(payload).execute()
                saved = (response.data or [payload])[0]
                audit_id = saved.get("id")
                if audit_id and audit_result.get("findings"):
                    self.save_findings(audit_result["findings"], audit_id, payload["property_id"], active_user_id)
                return saved
            except Exception as exc:
                logger.warning("Supabase save_audit error: %s", str(exc))
                raise RuntimeError(f"Failed to save audit to Supabase: {str(exc)}") from exc

        return payload

    def get_findings(self, audit_id: Optional[str] = None, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch findings for current user."""
        if self.demo_mode:
            records = list(get_demo_app_records()["findings"])
            if audit_id:
                records = [r for r in records if str(r.get("audit_id")) == str(audit_id)]
            if property_id:
                records = [r for r in records if str(r.get("property_id")) == str(property_id)]
            return records
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        try:
            query = self.client.table("findings").select("*").eq("user_id", active_user_id)
            if audit_id:
                query = query.eq("audit_id", audit_id)
            if property_id:
                query = query.eq("property_id", property_id)
            response = query.execute()
            return response.data or []
        except Exception as exc:
            logger.warning("Supabase get_findings error: %s", str(exc))
            return []

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
                "amount": float(finding.get("potential_recovery", 0.0)),
                "severity": finding.get("severity", "medium"),
                "status": "open",
                "created_at": now_iso,
                "updated_at": now_iso,
            }
            if active_user_id:
                item["user_id"] = active_user_id
            payloads.append(item)

        if self.demo_mode:
            return payloads

        if self.client is not None and active_user_id and payloads:
            try:
                response = self.client.table("findings").insert(payloads).execute()
                return response.data or payloads
            except Exception as exc:
                logger.warning("Supabase save_findings error: %s", str(exc))
                return payloads

        return payloads

    def save_risk_score(
        self,
        risk_result: Dict[str, Any],
        property_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save calculated risk score to Supabase database."""
        active_user_id = user_id or self.get_current_user_id()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "property_id": property_id,
            "score": float(risk_result.get("overall_score") or risk_result.get("risk_score", 0.0)),
            "risk_level": str(risk_result.get("risk_level", "Unassessed")),
            "summary": str(risk_result.get("summary", "")),
            "score_at": risk_result.get("timestamp", now_iso),
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.demo_mode:
            return {**payload, "id": "demo-risk-live"}

        if self.client is not None and active_user_id:
            try:
                response = self.client.table("risk_scores").insert(payload).execute()
                return (response.data or [payload])[0]
            except Exception as exc:
                logger.warning("Supabase save_risk_score error: %s", str(exc))
                return payload

        return payload

    def get_risk_scores(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch risk scores for current user."""
        if self.demo_mode:
            records = list(get_demo_app_records()["risk_scores"])
            if property_id:
                return [r for r in records if str(r.get("property_id")) == str(property_id)]
            return records
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        try:
            query = self.client.table("risk_scores").select("*").eq("user_id", active_user_id)
            if property_id:
                query = query.eq("property_id", property_id)
            response = query.execute()
            return response.data or []
        except Exception as exc:
            logger.warning("Supabase get_risk_scores error: %s", str(exc))
            return []

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
            "claim_amount": float(recovery_record.get("claim_amount") or recovery_record.get("potential_recovery", 0.0)),
            "recovered_amount": float(recovery_record.get("recovered_amount", 0.0)),
            "status": recovery_record.get("status", "Detected"),
            "notes": str(recovery_record.get("notes", "")),
            "created_at": recovery_record.get("created_at", now_iso),
            "updated_at": now_iso,
        }

        if active_user_id:
            payload["user_id"] = active_user_id

        if self.demo_mode:
            return {**payload, "id": "demo-recovery-live"}

        if self.client is not None and active_user_id:
            try:
                response = self.client.table("recovery_records").insert(payload).execute()
                return (response.data or [payload])[0]
            except Exception as exc:
                logger.warning("Supabase save_recovery_record error: %s", str(exc))
                return payload

        return payload

    def get_recovery_records(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch recovery records for current user."""
        if self.demo_mode:
            records = list(get_demo_app_records()["recovery_records"])
            if property_id:
                return [r for r in records if str(r.get("property_id")) == str(property_id)]
            return records
        active_user_id = self.get_current_user_id()
        if self.client is None or not active_user_id:
            return []

        try:
            query = self.client.table("recovery_records").select("*").eq("user_id", active_user_id)
            if property_id:
                query = query.eq("property_id", property_id)
            response = query.execute()
            return response.data or []
        except Exception as exc:
            logger.warning("Supabase get_recovery_records error: %s", str(exc))
            return []

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

        if self.demo_mode:
            payload["id"] = record_id
            return payload

        if self.client is not None:
            try:
                response = (
                    self.client.table("recovery_records")
                    .update(payload)
                    .eq("id", record_id)
                    .execute()
                )
                return (response.data or [payload])[0]
            except Exception as exc:
                logger.warning("Supabase update_recovery_status error: %s", str(exc))
                return payload

        payload["id"] = record_id
        return payload
