"""
LeaseGuard AI - Main Application Entry Point.
Commercial Lease Auditing & Financial Recovery Platform.
"""
from typing import Optional

import streamlit as st
from utils.css_loader import load_css
from services.auth import login_user, login_demo_account, logout_user, register_user

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
    settings,
)

# Navigation Mapping
PAGES = {
    "Dashboard": dashboard.render,
    "Properties": properties.render,
    "Documents": documents.render,
    "Audits": audits.render,
    "Findings": findings.render,
    "Risk Analysis": risk.render,
    "Recovery": recovery.render,
    "Disputes": disputes.render,
    "Analytics": analytics.render,
    "Settings": settings.render,
}

NAVIGATION_GROUPS = {
    "Overview": ["Dashboard"],
    "Portfolio": ["Properties", "Documents"],
    "Audit": ["Audits", "Findings", "Risk Analysis"],
    "Recovery": ["Recovery", "Disputes"],
    "Insights": ["Analytics"],
    "System": ["Settings"],
}


def _set_active_page(group: str) -> None:
    """Keep grouped sidebar radios acting as a single navigation control."""
    source_key = f"nav_{group.lower().replace(' ', '_')}"
    selected = st.session_state.get(source_key)
    if selected:
        st.session_state["active_page"] = selected
        for other_group in NAVIGATION_GROUPS:
            other_key = f"nav_{other_group.lower().replace(' ', '_')}"
            if other_key != source_key:
                st.session_state[other_key] = None


def render_auth_screen():
    """Render the standalone, unprotected authentication experience."""
    st.markdown(
        """
        <div class="lg-auth-brand">
            <div class="lg-auth-mark">LG</div>
            <div class="lg-auth-product">LeaseGuard <span>AI</span></div>
            <div class="lg-auth-tagline">Lease intelligence. Financial protection.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="auth_card"):
        login_tab, register_tab = st.tabs(["Sign In", "Create Account"])

        with login_tab:
            st.markdown("<div class='lg-auth-card-title'>Welcome back</div><div class='lg-auth-card-copy'>Sign in to your LeaseGuard account.</div>", unsafe_allow_html=True)
            email = st.text_input("Email address", key="auth_login_email", placeholder="name@company.com")

            show_login_password = st.session_state.get("show_login_password", False)
            pwd_col, eye_col = st.columns([5, 1])

            with pwd_col:
                password = st.text_input(
                    "Password",
                    type="default" if show_login_password else "password",
                    key="auth_login_password",
                    help="Use the eye icon to reveal or hide your password.",
                )
            with eye_col:
                if st.button("👁", key="toggle_login_password", help="Show or hide password"):
                    st.session_state["show_login_password"] = not show_login_password
                    st.rerun()

            if st.button("Sign In", use_container_width=True, type="primary"):
                try:
                    user = login_user(email, password)
                    st.session_state["authenticated_user"] = user
                    st.session_state["user_id"] = user.get("id")
                    if user.get("access_token"):
                        st.session_state["access_token"] = user.get("access_token")
                    if user.get("refresh_token"):
                        st.session_state["refresh_token"] = user.get("refresh_token")
                    st.rerun()
                except (ValueError, RuntimeError) as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Sign-in failed: {str(e)}")

        with register_tab:
            st.markdown("<div class='lg-auth-card-title'>Create your account</div><div class='lg-auth-card-copy'>Start reviewing lease compliance with LeaseGuard.</div>", unsafe_allow_html=True)
            reg_email = st.text_input("Email address", key="auth_register_email", placeholder="name@company.com")

            show_register_password = st.session_state.get("show_register_password", False)
            reg_pwd_col, reg_eye_col = st.columns([5, 1])
            with reg_pwd_col:
                reg_password = st.text_input(
                    "Password",
                    type="default" if show_register_password else "password",
                    key="auth_register_password",
                )
            with reg_eye_col:
                if st.button("👁", key="toggle_register_password", help="Show or hide password"):
                    st.session_state["show_register_password"] = not show_register_password
                    st.rerun()

            reg_confirm_pwd_col, reg_confirm_eye_col = st.columns([5, 1])
            with reg_confirm_pwd_col:
                reg_confirm = st.text_input(
                    "Confirm password",
                    type="default" if show_register_password else "password",
                    key="auth_register_confirm",
                )
            with reg_confirm_eye_col:
                if st.button("👁", key="toggle_register_confirm_password", help="Show or hide confirm password"):
                    st.session_state["show_register_password"] = not show_register_password
                    st.rerun()

            if st.button("Create Account", use_container_width=True, type="primary"):
                if reg_password != reg_confirm:
                    st.error("Passwords do not match. Please enter them again.")
                else:
                    try:
                        result = register_user(reg_email, reg_password)
                        if result.get("requires_confirmation"):
                            st.info("Account created. Please check your email and confirm your account before logging in.")
                        else:
                            user = result.get("user") or result
                            st.session_state["authenticated_user"] = user
                            st.session_state["user_id"] = user.get("id")
                            if result.get("access_token"):
                                st.session_state["access_token"] = result.get("access_token")
                            if result.get("refresh_token"):
                                st.session_state["refresh_token"] = result.get("refresh_token")
                            st.success("Account created successfully.")
                            st.rerun()
                    except (ValueError, RuntimeError) as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Account creation failed: {str(e)}")

    # --- Demo Account Section ---
    st.markdown("<div style='margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border);'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem; font-weight: 500;'>Try before signing up</div>", unsafe_allow_html=True)

    if st.button("✨ Explore Demo Workspace", use_container_width=True, key="demo_account_btn"):
        try:
            user = login_demo_account()
            st.session_state["authenticated_user"] = user
            st.session_state["user_id"] = user.get("id")
            st.session_state["access_token"] = user.get("access_token", "demo-access-token")
            st.session_state["refresh_token"] = user.get("refresh_token", "demo-refresh-token")
            st.success("Demo workspace loaded. Explore the complete LeaseGuard platform.")
            st.rerun()
        except ValueError as ve:
            st.info(f"ℹ️ Demo access is not configured on this deployment.")
        except RuntimeError as re:
            st.error("Unable to start the demo account. Please try again or sign up for an account.")

    st.markdown("<div class='lg-auth-footer'>Secure enterprise lease intelligence</div>", unsafe_allow_html=True)

def render_sidebar(current_user: Optional[dict]) -> Optional[str]:
    """Render the application sidebar and navigation selector based on auth state."""
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

        st.markdown("<div class='sidebar-user-label'>ACCOUNT</div>", unsafe_allow_html=True)
        st.caption(current_user.get("email", "Signed-in user"))
        if st.button("Logout", use_container_width=True):
            try:
                logout_user()
            except Exception:
                pass
            st.session_state.clear()
            st.rerun()

        active_page = st.session_state.get("active_page", "Dashboard")
        for group, page_names in NAVIGATION_GROUPS.items():
            st.markdown(f'<div class="sidebar-section-title">{group}</div>', unsafe_allow_html=True)
            selection = st.radio(
                group,
                page_names,
                index=page_names.index(active_page) if active_page in page_names else None,
                key=f"nav_{group.lower().replace(' ', '_')}",
                label_visibility="collapsed",
                on_change=_set_active_page,
                args=(group,),
            )
            if selection:
                active_page = selection
        st.session_state["active_page"] = active_page
        selected_page = active_page

        st.markdown("---")
        st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 0.8rem; line-height: 1.8; color: #94a3b8;">
                <div><span class="lg-status-dot lg-dot-green"></span> Engine: <strong style="color: #e2e8f0;">Online</strong></div>
                <div><span class="lg-status-dot lg-dot-green"></span> Database: <strong style="color: #e2e8f0;">Supabase Auth active</strong></div>
                <div><span class="lg-status-dot lg-dot-green"></span> AI Pipelines: <strong style="color: #e2e8f0;">Available</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-footer-box">
                <strong>LeaseGuard AI v1.0</strong><br>
                Commercial Lease Auditing Platform<br>
                <span style="color: #38bdf8; font-weight: 600;">Phase 5: Enterprise UI & Analytics</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page


def main():
    """Main routing controller enforcing global authentication protection."""
    from services.auth import require_auth
    current_user = require_auth()

    if not current_user:
        render_auth_screen()
        return

    selected_page_key = render_sidebar(current_user)

    render_func = PAGES.get(selected_page_key, dashboard.render)
    render_func()


if __name__ == "__main__":
    main()

