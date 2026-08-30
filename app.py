"""
LeaseGuard AI - Main Application Entry Point.
Commercial Lease Auditing & Financial Recovery Platform.
"""
import streamlit as st
from utils.css_loader import load_css

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


def render_sidebar() -> str:
    """Render the application sidebar and navigation selector."""
    with st.sidebar:
        # Branding Header
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

        st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
        
        # Navigation Radio Selector
        selected_page = st.radio(
            "Go to",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")

        # System Status Summary
        st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 0.8rem; line-height: 1.8; color: #475569;">
                <div><span class="lg-status-dot lg-dot-green"></span> Engine: <strong style="color: #0f172a;">Online</strong></div>
                <div><span class="lg-status-dot lg-dot-yellow"></span> Database: <span style="color: #64748b;">Standby</span></div>
                <div><span class="lg-status-dot lg-dot-yellow"></span> AI Pipelines: <span style="color: #64748b;">Scaffolded</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Footer Meta
        st.markdown(
            """
            <div class="sidebar-footer-box">
                <strong>LeaseGuard AI v0.1</strong><br>
                24-Hour Hackathon Build<br>
                <span style="color: #2563eb; font-weight: 600;">Phase 1: Foundation Ready</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page


def main():
    """Main routing controller."""
    selected_page_key = render_sidebar()
    
    # Execute selected page renderer
    render_func = PAGES.get(selected_page_key, dashboard.render)
    render_func()


if __name__ == "__main__":
    main()
