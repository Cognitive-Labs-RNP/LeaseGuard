"""
Settings Page for LeaseGuard AI.
System configuration, API key management, database connection status, and platform preferences.
"""

import os
import streamlit as st
from services.supabase import SupabaseService
from services.ai import AIService
from utils.ui import page_header, section_header


def render():
    """Render Settings and System Configuration view."""
    from services.auth import require_auth
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("System", "Settings", "Account context, secure provider configuration, database status, and diagnostics.")

    tab_account, tab_auth, tab1, tab2, tab3 = st.tabs(["Account", "Authentication", "AI Providers", "Supabase", "System Diagnostics"])

    with tab_account:
        section_header("Account", "Current application account context.")
        st.text_input("Signed-in email", value=user.get("email", ""), disabled=True)

    with tab_auth:
        section_header("Authentication", "LeaseGuard uses Supabase email authentication for sign-in and registration.")
        st.info("Use the sidebar Logout control to end this session. Authentication settings are managed in Supabase.")

    with tab1:
        section_header("AI Providers", "Configure RocketRide and the primary/fallback AI keys for this active session.")

        rr_key = st.text_input("RocketRide API Key", value=os.getenv("ROCKETRIDE_APIKEY", ""), type="password")
        gemini_key = st.text_input("Gemini API Key (Primary LLM)", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        groq_key = st.text_input("Groq API Key (Fallback LLM)", value=os.getenv("GROQ_API_KEY", ""), type="password")

        if st.button("Save API Credentials", type="primary"):
            os.environ["ROCKETRIDE_APIKEY"] = rr_key
            os.environ["GEMINI_API_KEY"] = gemini_key
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("API credentials saved for active session.")

    with tab2:
        section_header("Supabase", "Connection status for authentication and application records.")
        supabase_service = SupabaseService()
        is_cfg = supabase_service.is_configured()

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Supabase Project URL", value=os.getenv("SUPABASE_URL", "https://your-project.supabase.co"), disabled=True)
        with col2:
            st.text_input("Supabase Anon Key", value="••••••••••••••••••••", disabled=True)

        if is_cfg:
            st.success("✅ Supabase connection is active and configured.")
        else:
            st.warning("⚠️ Supabase credentials not set in environment. App running in local memory mode.")

    with tab3:
        section_header("System Diagnostics", "Operational status for the existing application services.")
        ai_service = AIService()

        diag_data = [
            {"Component": "Audit Engine", "Status": "Online (Deterministic)", "Version": "v4.0"},
            {"Component": "Risk Engine", "Status": "Online (Multi-Factor Scoring)", "Version": "v4.0"},
            {"Component": "Recovery Engine", "Status": "Online (Lifecycle Pipeline)", "Version": "v4.0"},
            {"Component": "RocketRide Cloud Client", "Status": "Connected" if ai_service.is_configured() else "Standby Mode", "Version": "v1.0"},
            {"Component": "Supabase Database", "Status": "Connected" if is_cfg else "Local Mode", "Version": "PostgreSQL 15"},
        ]

        st.table(diag_data)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
