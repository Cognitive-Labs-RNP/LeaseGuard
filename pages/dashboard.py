"""
Executive Dashboard Page for LeaseGuard AI.
Provides portfolio overview, audit highlights, and financial recovery metrics.
"""
import streamlit as st
import pandas as pd


def render():
    """Render the Executive Dashboard view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">🛡️ Executive Dashboard</div>
            <div class="lg-subtitle">Real-time lease auditing overview, recovery pipeline, and property portfolio metrics.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Top KPI Summary Cards ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="lg-metric-card">
                <div class="lg-metric-label">Properties Monitored</div>
                <div class="lg-metric-value">14</div>
                <div class="lg-metric-trend lg-trend-neutral">Across 4 regions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="lg-metric-card purple">
                <div class="lg-metric-label">Documents Ingested</div>
                <div class="lg-metric-value">128</div>
                <div class="lg-metric-trend lg-trend-neutral">42 Leases · 86 Invoices</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="lg-metric-card danger">
                <div class="lg-metric-label">Identified Overcharges</div>
                <div class="lg-metric-value">$184,250</div>
                <div class="lg-metric-trend lg-trend-up">↑ 23 Discrepancies flagged</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class="lg-metric-card success">
                <div class="lg-metric-label">Recovered to Date</div>
                <div class="lg-metric-value">$62,400</div>
                <div class="lg-metric-trend lg-trend-up">33.8% Recovery rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # --- Main Content Split ---
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### 📋 Recent Audit Activity")
        st.caption("Latest reconciliation runs between lease agreements and utility/CAM billing.")

        # Sample placeholder table for UI layout
        recent_audits = pd.DataFrame(
            [
                {
                    "Audit ID": "AUD-2026-001",
                    "Property": "Skyline Tower - Suite 400",
                    "Period": "Q1 2026",
                    "Status": "Discrepancy Found",
                    "Variance": "$14,820",
                },
                {
                    "Audit ID": "AUD-2026-002",
                    "Property": "Apex Logistics Hub",
                    "Period": "Jan 2026",
                    "Status": "Passed",
                    "Variance": "$0.00",
                },
                {
                    "Audit ID": "AUD-2026-003",
                    "Property": "Harbor Plaza - Retail B",
                    "Period": "Feb 2026",
                    "Status": "CAM Cap Exceeded",
                    "Variance": "$8,450",
                },
                {
                    "Audit ID": "AUD-2026-004",
                    "Property": "Beacon Medical Center",
                    "Period": "2025 Reconciliation",
                    "Status": "Under Review",
                    "Variance": "$31,200",
                },
            ]
        )
        st.dataframe(recent_audits, use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("### ⚡ Quick Navigation")
        qcol1, qcol2, qcol3 = st.columns(3)
        with qcol1:
            st.button("📄 Upload Documents", use_container_width=True)
        with qcol2:
            st.button("🔍 Run New Audit", use_container_width=True)
        with qcol3:
            st.button("✉️ Draft Dispute Letter", use_container_width=True)

    with right_col:
        st.markdown("### ⚙️ System Status")
        st.markdown(
            """
            <div class="lg-card">
                <div style="margin-bottom: 0.75rem;">
                    <div style="font-weight: 600; font-size: 0.85rem;">UI Scaffolding</div>
                    <span class="lg-badge lg-badge-green"><span class="lg-status-dot lg-dot-green"></span> Operational (Phase 1)</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <div style="font-weight: 600; font-size: 0.85rem;">Supabase Database</div>
                    <span class="lg-badge lg-badge-amber"><span class="lg-status-dot lg-dot-yellow"></span> Ready for Configuration</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <div style="font-weight: 600; font-size: 0.85rem;">RocketRide / Gemini AI</div>
                    <span class="lg-badge lg-badge-amber"><span class="lg-status-dot lg-dot-yellow"></span> Pipeline Scaffolded</span>
                </div>
                <div>
                    <div style="font-weight: 600; font-size: 0.85rem;">PDF Parser (PyMuPDF)</div>
                    <span class="lg-badge lg-badge-green"><span class="lg-status-dot lg-dot-green"></span> Engine Loaded</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 💡 Phase 1 Notice")
        st.info(
            "Welcome to the **LeaseGuard AI** foundation. The modular architecture, custom styling, service interfaces, and navigation structure are initialized.",
            icon="ℹ️"
        )


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
