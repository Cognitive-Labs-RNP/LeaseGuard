"""
LeaseGuard AI - Main Application Entry Point.
Commercial Lease Auditing & Financial Recovery Platform.
"""
import streamlit as st
from utils.css_loader import load_css
from services.auth import get_current_user, login_user, logout_user, register_user

# --- Page Configuration ---
st.set_page_config(
    page_title="LeaseGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Custom Design System CSS ---
load_css("assets/styles.css")

# --- Import Page Renderers ---
from pages import (
    dashboard,
    properties,
    documents,
    audits,
    findings,
    risk,
    recovery,
    disputes,
    analytics,
)

# Navigation Mapping
PAGES = {
    "📊 Dashboard": dashboard.render,
    "🏢 Property Portfolio": properties.render,
    "📁 Document Vault": documents.render,
    "🔍 Audit Sessions": audits.render,
    "⚠️ Findings & Overcharges": findings.render,
    "🛡️ Risk Analysis": risk.render,
    "💰 Recovery Tracker": recovery.render,
    "✉️ Dispute Letters": disputes.render,
    "📈 Analytics & Trends": analytics.render,
}


def render_auth_screen():
    """Display simple login/register UI for unauthenticated users."""
    st.title("LeaseGuard AI")
    st.caption("AI-Powered Lease Auditing & Financial Recovery")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        email = st.text_input("Email", key="auth_login_email")
        password = st.text_input("Password", type="password", key="auth_login_password")

        if st.button("Login", use_container_width=True, type="primary"):
            try:
                user = login_user(email, password)
                st.session_state["authenticated_user"] = user
                st.session_state["user_id"] = user.get("id")
                st.success("Login successful.")
                st.rerun()
            except Exception as exc:  # pragma: no cover - UI path
                st.error(str(exc))

    with register_tab:
        reg_email = st.text_input("Email", key="auth_register_email")
        reg_password = st.text_input("Password", type="password", key="auth_register_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="auth_register_confirm")

        if st.button("Register", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    user = register_user(reg_email, reg_password)
                    st.session_state["authenticated_user"] = user
                    st.session_state["user_id"] = user.get("id")
                    st.success("Registration successful. Please check your email to confirm the account.")
                    st.rerun()
                except Exception as exc:  # pragma: no cover - UI path
                    st.error(str(exc))


def render_sidebar() -> str:
    """Render the application sidebar and navigation selector."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-box">
                <div class="sidebar-brand-title">
                    <span>🛡️</span> LeaseGuard AI
                </div>
                <div class="sidebar-brand-desc">
                    AI-Powered Lease Auditing & Financial Recovery
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current_user = st.session_state.get("authenticated_user") or get_current_user()
        if current_user:
            st.caption(f"Signed in as: {current_user.get('email', 'User')}")
            if st.button("Logout", use_container_width=True):
                logout_user()
                st.session_state.pop("authenticated_user", None)
                st.session_state.pop("user_id", None)
                st.rerun()

        st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
        selected_page = st.radio(
            "Go to",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 0.8rem; line-height: 1.8; color: #475569;">
                <div><span class="lg-status-dot lg-dot-green"></span> Engine: <strong style="color: #0f172a;">Online</strong></div>
                <div><span class="lg-status-dot lg-dot-yellow"></span> Database: <span style="color: #64748b;">Supabase Auth ready</span></div>
                <div><span class="lg-status-dot lg-dot-yellow"></span> AI Pipelines: <span style="color: #64748b;">Scaffolded</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-footer-box">
                <strong>LeaseGuard AI v0.1</strong><br>
                24-Hour Hackathon Build<br>
                <span style="color: #2563eb; font-weight: 600;">Phase 2: Auth & Schema</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page


def main():
    """Main routing controller."""
    current_user = st.session_state.get("authenticated_user") or get_current_user()

    if not current_user:
        render_auth_screen()
        return

    st.session_state["authenticated_user"] = current_user
    st.session_state["user_id"] = current_user.get("id")

    selected_page_key = render_sidebar()
    render_func = PAGES.get(selected_page_key, dashboard.render)
    render_func()


if __name__ == "__main__":
    main()
