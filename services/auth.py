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

    return response.user


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

    return response.user


def logout_user() -> None:
    """Log out the currently authenticated user from Supabase Auth."""
    client = get_supabase_client()
    client.auth.sign_out()


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return the current authenticated user dictionary or None."""
    try:
        client = get_supabase_client()
        response = client.auth.get_user()
        user = getattr(response, "user", None)
        if user is None:
            return None
        if hasattr(user, "model_dump"):
            return user.model_dump()
        return dict(user)
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
