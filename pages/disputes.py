"""
Dispute Letters Page for LeaseGuard AI (Phase 5 Cleanup).
Generates evidence-backed landlord dispute letters via AI and provides human review/editing prior to export using Supabase records.
"""

import streamlit as st
from services.auth import require_auth
from services.ai import AIService
from services.supabase import SupabaseService


def render():
    """Render Dispute Letter Generator view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">✉️ Dispute Letter Generator</div>
            <div class="lg-subtitle">Generate evidence-backed landlord dispute notices via AI with mandatory human review before export.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    supabase = SupabaseService()
    findings_list = supabase.get_findings()

    if "target_dispute_finding" in st.session_state:
        target_f = st.session_state["target_dispute_finding"]
        if target_f not in findings_list:
            findings_list.insert(0, target_f)

    if not findings_list:
        st.info("No discrepancy findings available for dispute generation. Run an audit in 🔍 Audits to flag lease overcharges first.")
        return

    st.markdown("### 📄 Step 1: Select Discrepancy Finding")

    selected_idx = st.selectbox(
        "Target Discrepancy Finding",
        range(len(findings_list)),
        format_func=lambda i: f"{findings_list[i].get('property_id', 'Property')} - {findings_list[i].get('title') or findings_list[i].get('finding_type')} (${float(findings_list[i].get('amount', 0)):,.2f})"
    )

    finding = findings_list[selected_idx]

    col1, col2 = st.columns(2)
    with col1:
        landlord_name = st.text_input("Landlord Entity Name", placeholder="e.g. Commercial Property Management LLC")
    with col2:
        tenant_name = st.text_input("Tenant Entity Name", placeholder="e.g. Operations Tenant Inc.")

    gen_btn = st.button("✨ Generate AI Dispute Letter", type="primary", use_container_width=True)

    if gen_btn or "current_dispute_letter" not in st.session_state:
        ai_service = AIService()
        ctx = {
            "property_name": finding.get("property_id", "Property"),
            "landlord_name": landlord_name or "Landlord Entity",
            "tenant_name": tenant_name or "Tenant Entity"
        }
        finding_payload = {
            "category": finding.get("title") or finding.get("finding_type", "CAM Cap Exceeded"),
            "explanation": finding.get("description", "Overcharge flagged"),
            "potential_recovery": float(finding.get("amount", 0.0)),
            "billed_amount": float(finding.get("billed_amount", finding.get("amount", 0.0))),
            "allowed_amount": float(finding.get("allowed_amount", 0.0)),
            "lease_evidence": finding.get("lease_evidence", "Lease agreement terms"),
            "invoice_evidence": finding.get("invoice_evidence", "Billed invoice statement")
        }
        letter_text = ai_service.generate_dispute_letter(finding_payload, ctx)
        st.session_state["current_dispute_letter"] = letter_text

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### ✏️ Step 2: Human Review & Edit (Mandatory)")
    st.caption("Review and edit the generated dispute notice prior to formal export.")

    edited_letter = st.text_area(
        "Dispute Letter Content",
        value=st.session_state.get("current_dispute_letter", ""),
        height=380
    )

    st.markdown("### 📥 Step 3: Export & Download")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            "⬇️ Download Text File (.txt)",
            data=edited_letter,
            file_name=f"Dispute_Notice_{finding.get('id', '001')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with dcol2:
        st.download_button(
            "⬇️ Download Markdown (.md)",
            data=edited_letter,
            file_name=f"Dispute_Notice_{finding.get('id', '001')}.md",
            mime="text/markdown",
            use_container_width=True
        )


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
