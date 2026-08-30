"""
Financial Recovery Tracking Page for LeaseGuard AI.
Tracks overcharge recovery pipeline from identification to landlord settlement.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Financial Recovery Pipeline view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">💰 Financial Recovery Tracker</div>
            <div class="lg-subtitle">Track the lifecycle of disputed funds from initial audit finding to credited refund.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Pipeline stages overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """
            <div class="lg-metric-card">
                <div class="lg-metric-label">1. Identified</div>
                <div class="lg-metric-value">$184,250</div>
                <div class="lg-metric-trend lg-trend-neutral">14 claims pending action</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="lg-metric-card warning">
                <div class="lg-metric-label">2. Claimed (Disputed)</div>
                <div class="lg-metric-value">$78,100</div>
                <div class="lg-metric-trend lg-trend-neutral">5 formal letters issued</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="lg-metric-card purple">
                <div class="lg-metric-label">3. In Negotiation</div>
                <div class="lg-metric-value">$43,750</div>
                <div class="lg-metric-trend lg-trend-neutral">Landlord responses received</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            """
            <div class="lg-metric-card success">
                <div class="lg-metric-label">4. Settled / Recovered</div>
                <div class="lg-metric-value">$62,400</div>
                <div class="lg-metric-trend lg-trend-up">Credited to rent ledger</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Active Recovery Claims")

    recovery_data = pd.DataFrame([
        {
            "Claim ID": "REC-2026-01",
            "Property": "Skyline Commercial Center",
            "Dispute Reason": "Exceeded 5% Controllable CAM Cap",
            "Amount Claimed": "$6,200.00",
            "Letter Sent Date": "2026-08-10",
            "Stage": "In Negotiation",
            "Expected Resolution": "2026-09-15"
        },
        {
            "Claim ID": "REC-2026-02",
            "Property": "Skyline Commercial Center",
            "Dispute Reason": "Ineligible Rooftop HVAC Unit Replacement",
            "Amount Claimed": "$8,620.00",
            "Letter Sent Date": "2026-08-14",
            "Stage": "Letter Issued",
            "Expected Resolution": "2026-09-30"
        },
        {
            "Claim ID": "REC-2026-03",
            "Property": "Harbor Retail Plaza",
            "Dispute Reason": "Pro-Rata Denominator Misstatement",
            "Amount Claimed": "$2,954.00",
            "Letter Sent Date": "2026-07-28",
            "Stage": "Settled & Credited",
            "Expected Resolution": "Completed"
        }
    ])

    st.dataframe(recovery_data, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
