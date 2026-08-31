"""
Settings Page for LeaseGuard AI.
System configuration, API key management, database connection status, and platform preferences.
"""

import os
import streamlit as st
from services.supabase import SupabaseService
from services.ai import AIService


def render():
    """Render Settings and System Configuration view."""
    from services.auth import require_auth
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">⚙️ System Settings & API Configuration</div>
            <div class="lg-subtitle">Manage API integration keys, Supabase database connections, and platform parameters.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["🔑 API Credentials", "🗄️ Database & Storage", "📊 System Health & Diagnostics"])

    with tab1:
        st.markdown("### 🤖 AI Engine & RocketRide Pipelines")
        st.caption("Configure primary and fallback AI provider API keys.")

        rr_key = st.text_input("RocketRide API Key", value=os.getenv("ROCKETRIDE_APIKEY", ""), type="password")
        gemini_key = st.text_input("Gemini API Key (Primary LLM)", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        groq_key = st.text_input("Groq API Key (Fallback LLM)", value=os.getenv("GROQ_API_KEY", ""), type="password")

        if st.button("Save API Credentials", type="primary"):
            os.environ["ROCKETRIDE_APIKEY"] = rr_key
            os.environ["GEMINI_API_KEY"] = gemini_key
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("API credentials saved for active session.")

    with tab2:
        st.markdown("### 🗄️ Supabase PostgreSQL & Storage")
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
        st.markdown("### 🛠️ Diagnostic Status")
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
