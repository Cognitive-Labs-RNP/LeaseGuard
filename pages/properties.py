"""
Properties Management Page for LeaseGuard AI.
Allows viewing, registering, and managing commercial real estate properties.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Properties Management view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">🏢 Property Portfolio</div>
            <div class="lg-subtitle">Manage commercial properties, lease contracts, and assigned landlords.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Actions bar
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.text_input("🔍 Search properties by name, code, or address...", placeholder="e.g. Skyline Tower", label_visibility="collapsed")
    with top_col2:
        st.button("➕ Add New Property", use_container_width=True, type="primary")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Properties overview
    sample_properties = pd.DataFrame([
        {
            "Property Code": "PROP-001",
            "Name": "Skyline Commercial Center",
            "Address": "100 Financial Way, New York, NY",
            "Square Footage": "45,000 sq ft",
            "Active Leases": 3,
            "Risk Tier": "Low",
            "Status": "Active"
        },
        {
            "Property Code": "PROP-002",
            "Name": "Apex Logistics Hub",
            "Address": "500 Freight Lane, Dallas, TX",
            "Square Footage": "120,000 sq ft",
            "Active Leases": 1,
            "Risk Tier": "Low",
            "Status": "Active"
        },
        {
            "Property Code": "PROP-003",
            "Name": "Harbor Retail Plaza",
            "Address": "12 Ocean Blvd, Miami, FL",
            "Square Footage": "28,500 sq ft",
            "Active Leases": 2,
            "Risk Tier": "Moderate",
            "Status": "Active"
        },
        {
            "Property Code": "PROP-004",
            "Name": "Beacon Medical Center",
            "Address": "77 Health Park Dr, Boston, MA",
            "Square Footage": "62,000 sq ft",
            "Active Leases": 4,
            "Risk Tier": "High",
            "Status": "Audit Required"
        }
    ])

    st.dataframe(sample_properties, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="lg-placeholder-box">
            <div class="lg-placeholder-title">Database Integration Scheduled</div>
            <div class="lg-placeholder-desc">
                In the upcoming database phase, properties will be synchronized with Supabase PostgreSQL and linked directly to lease agreement documents and billing ledgers.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
