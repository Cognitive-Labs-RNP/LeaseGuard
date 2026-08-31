"""Supabase Authentication helpers for LeaseGuard AI."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def get_supabase_client() -> Client:
    """Return the configured Supabase client for Auth and PostgREST access."""
    url = (os.getenv("SUPABASE_URL") or "").strip()
    key = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()

    if not url or not key:
        raise RuntimeError("Missing Supabase configuration. Set SUPABASE_URL and SUPABASE_KEY in your .env file.")

    return create_client(url, key)


def _user_to_dict(user: Any) -> Dict[str, Any]:
    """Convert Supabase User object or dict to standard python dictionary."""
    if user is None:
        return {}
    if isinstance(user, dict):
        return user
    if hasattr(user, "model_dump"):
        return user.model_dump()
    res = {}
    if hasattr(user, "id"):
        res["id"] = user.id
    if hasattr(user, "email"):
        res["email"] = user.email
    return res


def register_user(email: str, password: str) -> Dict[str, Any]:
    """Register a new user via Supabase Email authentication."""
    email = (email or "").strip()
    password = password or ""

    if not email or not password:
        raise ValueError("Email and password are required.")

    client = get_supabase_client()
    response = client.auth.sign_up({"email": email, "password": password})

    if response.user is None:
        raise RuntimeError("Registration failed. Please check your email and password.")

    return _user_to_dict(response.user)


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user via Supabase Email/password login."""
    email = (email or "").strip()
    password = password or ""

    if not email or not password:
        raise ValueError("Email and password are required.")

    client = get_supabase_client()
    response = client.auth.sign_in_with_password({"email": email, "password": password})

    if response.user is None:
        raise RuntimeError("Invalid email or password.")

    return _user_to_dict(response.user)


def login_demo_account() -> Dict[str, Any]:
    """Authenticate the preconfigured demo account via Supabase Email/password login.
    
    This function reads DEMO_EMAIL and DEMO_PASSWORD from environment variables
    and attempts to authenticate with Supabase using those credentials.
    
    Returns:
        Dict with user info if successful.
        
    Raises:
        ValueError: If demo credentials are not configured.
        RuntimeError: If authentication fails.
    """
    demo_email = (os.getenv("DEMO_EMAIL") or "").strip()
    demo_password = (os.getenv("DEMO_PASSWORD") or "").strip()

    if not demo_email or not demo_password:
        raise ValueError(
            "Demo account credentials are not configured. "
            "Add DEMO_EMAIL and DEMO_PASSWORD to your .env file."
        )

    try:
        user = login_user(demo_email, demo_password)
        return user
    except Exception as exc:
        raise RuntimeError(
            "Demo account login failed. Ensure the demo account exists in Supabase "
            "and credentials are correct in your .env file."
        ) from exc


def logout_user() -> None:
    """Log out the currently authenticated user from Supabase Auth."""
    if (os.getenv("DEMO_MODE") or "").strip().lower() in {"1", "true", "yes", "on", "demo"}:
        return
    client = get_supabase_client()
    client.auth.sign_out()


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return the current authenticated user dictionary or None."""
    if (os.getenv("DEMO_MODE") or "").strip().lower() in {"1", "true", "yes", "on", "demo"}:
        return {"id": "demo-user-001", "email": "demo@leaseguard.ai"}
    try:
        client = get_supabase_client()
        response = client.auth.get_user()
        user = getattr(response, "user", None)
        if user is None:
            return None
        return _user_to_dict(user)
    except Exception:
        return None


def get_authenticated_user_id() -> Optional[str]:
    """Return the currently authenticated user's UUID or None."""
    user = get_current_user()
    if user is None:
        return None
    return user.get("id")


def require_authenticated_user_id() -> str:
    """Raise a clear error if the current user is not authenticated."""
    user_id = get_authenticated_user_id()
    if user_id is None:
        raise PermissionError("Authentication required. Please log in.")
    return user_id


def require_auth() -> Optional[Dict[str, Any]]:
    """Return authenticated user dictionary or None if unauthenticated."""
    import streamlit as st

    user = st.session_state.get("authenticated_user")
    if not user:
        user = get_current_user()
        if user:
            st.session_state["authenticated_user"] = user
            st.session_state["user_id"] = user.get("id")

    return user

