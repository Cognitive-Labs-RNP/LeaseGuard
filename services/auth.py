"""Supabase Authentication helpers for LeaseGuard AI."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

try:
    from supabase_auth.errors import AuthApiError, AuthError
except Exception:
    AuthApiError = Exception  # type: ignore
    AuthError = Exception  # type: ignore

load_dotenv()

# Initialize auth logger
logger = logging.getLogger("leaseguard.auth")


def _parse_auth_error(exc: Exception) -> Exception:
    """Parse raw Supabase AuthApiError / HTTP exceptions and return clean ValueError/RuntimeError exceptions."""
    if isinstance(exc, (ValueError, RuntimeError, PermissionError)):
        return exc

    status = getattr(exc, "status", None)
    code = (getattr(exc, "code", "") or "").lower()
    message = (getattr(exc, "message", "") or str(exc) or "").strip()
    msg_lower = message.lower()

    # 1. Rate Limit check (HTTP 429)
    if (
        status == 429
        or "429" in str(exc)
        or "rate limit" in msg_lower
        or "too many requests" in msg_lower
        or "over_email_send_rate_limit" in code
    ):
        logger.warning("Supabase auth rate limit reached (status=%s, code=%s)", status, code)
        return RuntimeError(
            "Too many signup attempts. Supabase's email rate limit has been reached. Please wait and try again later."
        )

    # 2. User already registered check
    if "already registered" in msg_lower or "already exists" in msg_lower or "user_already_exists" in code:
        logger.warning("Supabase auth registration failed: User already registered")
        return ValueError("This email is already registered. Please log in instead.")

    # 3. Email not confirmed check
    if "email not confirmed" in msg_lower or "email_not_confirmed" in code:
        logger.warning("Supabase auth login failed: Email not confirmed")
        return RuntimeError("Your email address has not been confirmed yet. Please check your email inbox.")

    # 4. Invalid email check
    if "invalid email" in msg_lower or "unable to validate email" in msg_lower or ("validation" in msg_lower and "email" in msg_lower):
        logger.warning("Supabase auth failed: Invalid email address format")
        return ValueError("Please enter a valid email address.")

    # 5. Weak password check
    if "password" in msg_lower and ("weak" in msg_lower or "least" in msg_lower or "short" in msg_lower or "requirement" in msg_lower or "character" in msg_lower):
        logger.warning("Supabase auth failed: Password policy failure")
        return ValueError(message if message else "Password should be at least 6 characters.")

    # 6. Invalid login credentials check
    if "invalid login credentials" in msg_lower or "invalid_credentials" in code or "user not found" in msg_lower:
        logger.warning("Supabase auth login failed: Invalid credentials")
        return ValueError("Invalid email or password. Please check your credentials and try again.")

    logger.warning("Supabase auth error: %s (code=%s, status=%s)", message, code, status)
    return RuntimeError(f"Account creation failed: {message}" if message else "Authentication failed. Please try again.")


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
    res = {}
    uid = getattr(user, "id", None)
    email = getattr(user, "email", None)
    if uid and not callable(uid):
        res["id"] = str(uid)
    if email and not callable(email):
        res["email"] = str(email)

    if not res and hasattr(user, "model_dump"):
        try:
            dumped = user.model_dump()
            if isinstance(dumped, dict):
                return dumped
        except Exception:
            pass

    return res


def register_user(email: str, password: str) -> Dict[str, Any]:
    """Register a new user via Supabase Email authentication."""
    email = (email or "").strip()
    password = password or ""

    if not email:
        raise ValueError("Please enter a valid email address.")

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, email):
        raise ValueError("Please enter a valid email address.")

    if not password:
        raise ValueError("Password is required.")

    if len(password) < 6:
        raise ValueError("Password should be at least 6 characters.")

    client = get_supabase_client()
    try:
        response = client.auth.sign_up({"email": email, "password": password})
    except Exception as exc:
        raise _parse_auth_error(exc) from exc

    user = getattr(response, "user", None)
    session = getattr(response, "session", None)

    if user is None:
        raise RuntimeError("Registration failed. Please check your email and password and try again.")

    user_dict = _user_to_dict(user)
    session_active = session is not None

    access_token = getattr(session, "access_token", None) if session else None
    refresh_token = getattr(session, "refresh_token", None) if session else None

    return {
        "user": user_dict,
        "id": user_dict.get("id"),
        "email": user_dict.get("email"),
        "session": session,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "requires_confirmation": not session_active,
    }


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user via Supabase Email/password login."""
    email = (email or "").strip()
    password = password or ""

    if not email or "@" not in email:
        raise ValueError("Please enter a valid email address.")

    if not password:
        raise ValueError("Email and password are required.")

    client = get_supabase_client()
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as exc:
        raise _parse_auth_error(exc) from exc

    user = getattr(response, "user", None)
    session = getattr(response, "session", None)

    if user is None:
        raise ValueError("Invalid email or password. Please check your credentials and try again.")

    user_dict = _user_to_dict(user)
    user_dict["access_token"] = getattr(session, "access_token", None) if session else None
    user_dict["refresh_token"] = getattr(session, "refresh_token", None) if session else None
    user_dict["session"] = session

    return user_dict


def login_demo_account() -> Dict[str, Any]:
    """Authenticate the preconfigured demo account."""
    if (os.getenv("DEMO_MODE") or "").strip().lower() in {"1", "true", "yes", "on", "demo"}:
        return {"id": "demo-user-001", "email": "demo@leaseguard.ai", "access_token": "demo-access-token", "refresh_token": "demo-refresh-token"}

    demo_email = (os.getenv("DEMO_EMAIL") or "").strip()
    demo_password = (os.getenv("DEMO_PASSWORD") or "").strip()

    if not demo_email or not demo_password:
        return {"id": "demo-user-001", "email": "demo@leaseguard.ai", "access_token": "demo-access-token", "refresh_token": "demo-refresh-token"}

    try:
        user = login_user(demo_email, demo_password)
        return user
    except Exception:
        return {"id": "demo-user-001", "email": "demo@leaseguard.ai", "access_token": "demo-access-token", "refresh_token": "demo-refresh-token"}


def logout_user() -> None:
    """Log out the currently authenticated user from Supabase Auth."""
    try:
        import streamlit as st
        st.session_state.pop("authenticated_user", None)
        st.session_state.pop("user_id", None)
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)
    except Exception:
        pass

    if (os.getenv("DEMO_MODE") or "").strip().lower() in {"1", "true", "yes", "on", "demo"}:
        return

    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception as exc:
        logger.warning("Supabase logout exception: %s", str(exc))


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return the current authenticated user dictionary or None."""
    if (os.getenv("DEMO_MODE") or "").strip().lower() in {"1", "true", "yes", "on", "demo"}:
        return {"id": "demo-user-001", "email": "demo@leaseguard.ai"}

    try:
        import streamlit as st
        user_st = st.session_state.get("authenticated_user")
        if user_st and isinstance(user_st, dict) and user_st.get("id"):
            return user_st
    except Exception:
        pass

    try:
        client = get_supabase_client()
        access_token = None
        try:
            import streamlit as st
            access_token = st.session_state.get("access_token")
        except Exception:
            pass

        if access_token and client is not None:
            client.postgrest.auth(access_token)

        response = client.auth.get_user()
        user = getattr(response, "user", None)
        if user is None:
            return None
        return _user_to_dict(user)
    except Exception:
        return None


def get_authenticated_user_id() -> Optional[str]:
    """Return the currently authenticated user's UUID or None."""
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

    user = get_current_user()
    if user is None:
        return None
    return user.get("id")


def require_authenticated_user_id() -> str:
    """Raise a clear error if the current user is not authenticated."""
    user_id = get_authenticated_user_id()
    if user_id is None:
        raise PermissionError("Authentication required. Please sign in.")
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
