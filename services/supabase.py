"""Supabase database client service for LeaseGuard AI."""

from __future__ import annotations

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

        if self.url and self.key:
            self.client = create_client(self.url, self.key)

    def is_configured(self) -> bool:
        """Check if Supabase credentials are configured."""
        return bool(self.url and self.key and "your-project" not in self.url)

    def get_current_user_id(self) -> str:
        """Return the authenticated user's ID for all user-scoped queries."""
        return require_authenticated_user_id()

    def get_properties(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch properties belonging to the currently authenticated user."""
        active_user_id = user_id or self.get_current_user_id()
        if self.client is None:
            return []

        response = self.client.table("properties").select("*").eq("user_id", active_user_id).execute()
        return response.data or []

    def create_property(self, property_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a property and always associate it with the authenticated user."""
        active_user_id = user_id or self.get_current_user_id()
        if self.client is None:
            return {}

        payload = dict(property_data)
        payload["user_id"] = active_user_id
        response = self.client.table("properties").insert(payload).execute()
        return (response.data or [{}])[0]

    def get_documents(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch uploaded lease or invoice documents for the current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None:
            return []

        query = self.client.table("documents").select("*").eq("user_id", active_user_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def get_audits(self, property_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch audits for the current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None:
            return []

        query = self.client.table("audits").select("*").eq("user_id", active_user_id)
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data or []

    def get_findings(self, audit_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch findings for the current user."""
        active_user_id = self.get_current_user_id()
        if self.client is None:
            return []

        query = self.client.table("findings").select("*").eq("user_id", active_user_id)
        if audit_id:
            query = query.eq("audit_id", audit_id)
        response = query.execute()
        return response.data or []
