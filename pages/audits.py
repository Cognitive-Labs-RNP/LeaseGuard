"""
Audit Sessions Page for LeaseGuard AI.
Configures and launches reconciliation sessions between lease rules and invoice charges.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Audit Sessions view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">🔍 Audit Sessions</div>
            <div class="lg-subtitle">Configure and run lease-to-invoice reconciliation workflows.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🚀 Launch New Audit Session")
    with st.container():
        st.markdown('<div class="lg-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.selectbox("Select Target Property", ["PROP-001 - Skyline Commercial Center", "PROP-002 - Apex Logistics Hub", "PROP-003 - Harbor Retail Plaza"])
        with col2:
            st.selectbox("Select Active Lease Baseline", ["Skyline_Master_Lease_2024.pdf (DOC-L-01)", "Skyline_Amendment_1.pdf"])
        with col3:
            st.selectbox("Select Invoice / Reconciliation Statement", ["Skyline_2025_CAM_Reconciliation.pdf (DOC-I-14)", "Q1_2026_Utility_Bill.pdf"])

        audit_btn = st.button("▶️ Execute Audit Engine", type="primary", use_container_width=True)
        if audit_btn:
            st.info("Audit engine pipeline will execute reconciliation logic in Phase 3.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Historical Audit Sessions")

    audit_history = pd.DataFrame([
        {
            "Audit ID": "AUD-2026-001",
            "Property": "Skyline Commercial Center",
            "Lease Document": "Skyline_Master_Lease_2024.pdf",
            "Invoice Document": "Skyline_2025_CAM_Reconciliation.pdf",
            "Date Run": "2026-08-25",
            "Discrepancies Flagged": 3,
            "Potential Overcharge": "$14,820.00",
            "Status": "Review Ready"
        },
        {
            "Audit ID": "AUD-2026-002",
            "Property": "Apex Logistics Hub",
            "Lease Document": "Apex_Master_Lease_2023.pdf",
            "Invoice Document": "Apex_Q2_2026_Operating.pdf",
            "Date Run": "2026-08-24",
            "Discrepancies Flagged": 0,
            "Potential Overcharge": "$0.00",
            "Status": "Verified Clean"
        }
    ])

    st.dataframe(audit_history, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
