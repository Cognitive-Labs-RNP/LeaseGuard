"""
Audit Findings & Overcharges Page for LeaseGuard AI.
Displays itemized discrepancies, clause violations, and financial calculations.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Audit Findings view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">⚠️ Audit Findings & Overcharges</div>
            <div class="lg-subtitle">Detailed itemized discrepancies, lease clause violations, and financial variance.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        st.selectbox("Filter by Property", ["All Properties", "Skyline Commercial Center", "Harbor Retail Plaza"])
    with filter_col2:
        st.selectbox("Filter by Finding Category", ["All Categories", "CAM Cap Violation", "Excluded Expense (Capital Item)", "Pro-rata Share Error", "Administrative Fee Markup"])
    with filter_col3:
        st.selectbox("Filter by Status", ["All Statuses", "Unclaimed", "Drafted in Dispute", "Recovered"])

    findings_data = pd.DataFrame([
        {
            "Finding ID": "FND-101",
            "Property": "Skyline Commercial",
            "Category": "CAM Cap Violation",
            "Clause Ref": "Section 4.2 (5% Controllable Cap)",
            "Billed Amount": "$48,200",
            "Allowed Max": "$42,000",
            "Overcharge Amount": "$6,200.00",
            "Confidence": "High (98%)",
            "Status": "Unclaimed"
        },
        {
            "Finding ID": "FND-102",
            "Property": "Skyline Commercial",
            "Category": "Capital Expenditure Exclusion",
            "Clause Ref": "Section 4.3 (Structural HVAC Exclusion)",
            "Billed Amount": "$8,620",
            "Allowed Max": "$0",
            "Overcharge Amount": "$8,620.00",
            "Confidence": "High (95%)",
            "Status": "Dispute Drafted"
        },
        {
            "Finding ID": "FND-103",
            "Property": "Harbor Retail Plaza",
            "Category": "Pro-Rata Share Miscalculation",
            "Clause Ref": "Exhibit B (12.4% vs 14.1% billed)",
            "Billed Amount": "$24,500",
            "Allowed Max": "$21,546",
            "Overcharge Amount": "$2,954.00",
            "Confidence": "High (92%)",
            "Status": "Unclaimed"
        }
    ])

    st.dataframe(findings_data, use_container_width=True, hide_index=True)

    st.markdown("### 🔎 Finding Evidence Inspector")
    with st.expander("Inspect FND-102: Capital Expenditure Exclusion ($8,620.00)", expanded=True):
        st.markdown(
            """
            <div class="lg-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <strong>Violation: Ineligible Capital Replacement Invoiced as Operating Maintenance</strong>
                    <span class="lg-badge lg-badge-red">Overcharge: $8,620.00</span>
                </div>
                <p style="font-size: 0.88rem; color: #475569; margin-bottom: 0.5rem;">
                    <strong>Lease Rule (Section 4.3):</strong> "Operating expenses shall explicitly exclude any capital improvements, structural replacements, or roof/chiller replacements exceeding $5,000 amortizable life."
                </p>
                <p style="font-size: 0.88rem; color: #475569;">
                    <strong>Invoice Line Item (Inv #2025-992):</strong> "Full replacement of central rooftop condenser unit - Unit 4: $8,620.00"
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
