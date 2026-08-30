"""
Risk Analysis Page for LeaseGuard AI.
Evaluates lease contract ambiguity, exposure to overcharges, and property risk ratings.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Risk Analysis view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">🛡️ Lease & Portfolio Risk Analysis</div>
            <div class="lg-subtitle">Assess contract ambiguity, audit vulnerability scores, and financial exposure risk.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rcol1, rcol2, rcol3 = st.columns(3)
    with rcol1:
        st.markdown(
            """
            <div class="lg-metric-card warning">
                <div class="lg-metric-label">Average Portfolio Risk</div>
                <div class="lg-metric-value">58 / 100</div>
                <div class="lg-metric-trend lg-trend-neutral">Moderate Exposure</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rcol2:
        st.markdown(
            """
            <div class="lg-metric-card danger">
                <div class="lg-metric-label">High-Risk Contracts</div>
                <div class="lg-metric-value">4 Leases</div>
                <div class="lg-metric-trend lg-trend-down">Uncapped CAM clauses</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rcol3:
        st.markdown(
            """
            <div class="lg-metric-card success">
                <div class="lg-metric-label">Audited Safeguard Rate</div>
                <div class="lg-metric-value">82%</div>
                <div class="lg-metric-trend lg-trend-up">Coverage across top leases</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Lease Risk Scorecard")

    risk_table = pd.DataFrame([
        {
            "Property / Lease": "Skyline Commercial Center - Unit 400",
            "Risk Score": "78 / 100",
            "Risk Tier": "High Risk",
            "Key Vulnerability": "Uncapped capital repairs & subjective management fee allocations",
            "Recommended Action": "Demand itemized vendor receipts"
        },
        {
            "Property / Lease": "Beacon Medical Center - Suite A",
            "Risk Score": "65 / 100",
            "Risk Tier": "Moderate Risk",
            "Key Vulnerability": "Ambiguous gross-up calculation method",
            "Recommended Action": "Clarify base-year occupancy adjustment"
        },
        {
            "Property / Lease": "Apex Logistics Hub",
            "Risk Score": "22 / 100",
            "Risk Tier": "Low Risk",
            "Key Vulnerability": "Strict 3% cumulative CAM cap with clear audit rights",
            "Recommended Action": "Standard annual check"
        }
    ])

    st.dataframe(risk_table, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="lg-placeholder-box">
            <div class="lg-placeholder-title">Risk Scoring Engine</div>
            <div class="lg-placeholder-desc">
                In the Risk Engine phase, multi-factor scoring algorithms will evaluate lease clauses against historical dispute data to produce quantitative risk indices.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
