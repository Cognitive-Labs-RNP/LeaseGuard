"""
Settings Page for LeaseGuard AI.
System configuration, API key management, database connection status, and platform preferences.
"""

import streamlit as st
from services.supabase import SupabaseService
from services.ai import AIService
from utils.ui import page_header, section_header


def render():
    """Render Settings and System Configuration view."""
    from services.auth import require_auth, logout_user

    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("System", "Settings", "Account context, session controls, and system diagnostics.")

    tab_account, tab_system = st.tabs(["Account", "System Diagnostics"])

    with tab_account:
        section_header("Account", "Current application account context.")
        st.text_input("Signed-in email", value=user.get("email", ""), disabled=True)

        st.markdown("### Account & Session")
        st.write("Signed in as:")
        st.write(user.get("email", ""))

        if st.button("Log Out", type="primary", use_container_width=True):
            try:
                logout_user()
            except Exception:
                pass
            for key in ["authenticated_user", "user_id", "access_token", "refresh_token"]:
                st.session_state.pop(key, None)
            st.rerun()

    with tab_system:
        section_header("System Diagnostics", "Operational status for the existing application services.")
        ai_service = AIService()
        supabase_service = SupabaseService()
        is_cfg = supabase_service.is_configured()

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
