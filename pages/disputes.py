"""
Dispute Letter Generator Page for LeaseGuard AI.
Generates contractual audit dispute letters for landlord communication.
"""
import streamlit as st


def render():
    """Render Dispute Letter Generator view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">✉️ Dispute Letter Generator</div>
            <div class="lg-subtitle">Draft legally precise audit dispute letters backed by lease clause references.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_form, col_preview = st.columns([1, 1])

    with col_form:
        st.markdown("### 📝 Dispute Parameters")
        with st.container():
            st.markdown('<div class="lg-card">', unsafe_allow_html=True)
            prop_choice = st.selectbox(
                "Select Property",
                ["PROP-001 - Skyline Commercial Center", "PROP-003 - Harbor Retail Plaza", "PROP-004 - Beacon Medical Center"]
            )
            finding_target = st.multiselect(
                "Select Findings to Include in Dispute",
                [
                    "FND-101: CAM Cap Violation ($6,200.00)",
                    "FND-102: Capital Expenditure Exclusion ($8,620.00)",
                    "FND-103: Pro-Rata Share Error ($2,954.00)"
                ],
                default=["FND-101: CAM Cap Violation ($6,200.00)", "FND-102: Capital Expenditure Exclusion ($8,620.00)"]
            )
            recipient_name = st.text_input("Landlord / Property Manager Name", value="Horizon Properties Management LLC")
            tone_style = st.selectbox("Letter Tone", ["Collaborative & Professional", "Formal Contractual Notice", "Urgent / Escalated Notice"])
            
            gen_btn = st.button("✨ Draft Dispute Letter", type="primary", use_container_width=True)
            if gen_btn:
                st.info("LLM letter synthesis will be powered by the RocketRide/Gemini pipeline in the AI phase.")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown("### 📄 Letter Preview")
        preview_text = f"""**VIA CERTIFIED MAIL & EMAIL**

**Date:** August 30, 2026
**To:** {recipient_name}
**Re:** Notice of Operating Expense Discrepancies & Audit Findings - Skyline Commercial Center

Dear Horizon Properties Management,

Pursuant to Section 4.2 of the Master Lease Agreement dated January 15, 2024, between Skyline Properties LLC ("Landlord") and Tenant, we have conducted a compliance review of the 2025 Common Area Maintenance (CAM) reconciliation statement.

Our audit identified the following billing variances totaling **$14,820.00** in overcharges:

1. **Controllable Expense Cap Exceeded ($6,200.00):** Section 4.2 establishes a strict 5% annual cumulative cap on controllable operating costs.
2. **Ineligible Capital Replacement ($8,620.00):** Section 4.3 specifically excludes structural HVAC replacements exceeding $5,000 from operating expenses.

Please review the attached reconciliation exhibits and apply a billing credit of **$14,820.00** toward our upcoming rent payment.

Sincerely,
Lease Administration & Audit Team
"""
        st.text_area("Generated Draft", value=preview_text, height=360)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.button("📥 Export PDF (ReportLab)", use_container_width=True)
        with btn_col2:
            st.button("📋 Copy to Clipboard", use_container_width=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
