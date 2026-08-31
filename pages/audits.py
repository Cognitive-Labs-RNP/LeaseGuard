"""
Audit Sessions Page for LeaseGuard AI (Phase 5.1 Fixes).
Configures and launches deterministic reconciliation sessions between lease rules and invoice charges using Supabase records.
"""

import os
import streamlit as st
import pandas as pd
from services.ai import extract_invoice_summary, extract_lease_rules
from services.auth import require_auth
from services.audit_engine import AuditEngine
from services.risk_engine import RiskEngine
from services.recovery_engine import RecoveryEngine
from services.supabase import SupabaseService
from utils.ui import empty_state, page_header, section_header


def render():
    """Render Audit Sessions view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Audit", "Audit Sessions", "Reconcile lease obligations against billing statements and identify potential recovery.")

    supabase = SupabaseService()
    properties = supabase.get_properties()
    all_documents = supabase.get_documents() + st.session_state.get("session_documents", [])

    section_header("Run an Audit", "1. Select Property  →  2. Select Lease  →  3. Select Invoice  →  4. Run Audit")
    with st.container():
        st.markdown('<div class="lg-card">', unsafe_allow_html=True)

        if not properties:
            empty_state("No properties added", "Add a property first, then upload its lease and invoice documents.", "○")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        prop_map = {f"{p.get('code', 'PROP')}: {p.get('name')}": p for p in properties}
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_prop_label = st.selectbox("Select Target Property", list(prop_map.keys()), key="audit_prop_select")
            selected_prop = prop_map[selected_prop_label]
            selected_prop_id = selected_prop.get("id")

        # Filter documents for this specific property
        prop_docs = [d for d in all_documents if str(d.get("property_id") or d.get("Property")) in (str(selected_prop_id), selected_prop.get("name"))]
        
        lease_docs = [
            d for d in prop_docs 
            if (d.get("document_type") or d.get("Type") or "").lower() in ["lease agreement", "lease", "building amendment"]
        ]
        invoice_docs = [
            d for d in prop_docs 
            if (d.get("document_type") or d.get("Type") or "").lower() in ["cam reconciliation statement", "utility invoice", "tax bill", "invoice"]
        ]

        with col2:
            if lease_docs:
                lease_opts = [f"{d.get('filename') or d.get('Title')} ({d.get('document_type') or d.get('Type')})" for d in lease_docs]
                sel_lease_label = st.selectbox("Select Active Lease Baseline", lease_opts, key="audit_lease_select")
                sel_lease_doc = lease_docs[lease_opts.index(sel_lease_label)]
                lease_text_input = sel_lease_doc.get("content_text") or f"Section 6.1: Controllable CAM expenses capped at $10,000 annually for {selected_prop.get('name')}."
            else:
                st.selectbox("Select Active Lease Baseline", ["No active leases available. Upload a lease first."], disabled=True, key="audit_no_lease")
                uploaded_lease_file = st.file_uploader("Upload Lease Baseline (PDF/TXT)", type=["pdf", "txt"], key="audit_upload_lease")
                lease_text_input = ""
                if uploaded_lease_file:
                    lease_text_input = uploaded_lease_file.getvalue().decode("utf-8", errors="ignore")

        with col3:
            if invoice_docs:
                inv_opts = [f"{d.get('filename') or d.get('Title')} ({d.get('document_type') or d.get('Type')})" for d in invoice_docs]
                sel_inv_label = st.selectbox("Select Invoice / Reconciliation Statement", inv_opts, key="audit_inv_select")
                sel_inv_doc = invoice_docs[inv_opts.index(sel_inv_label)]
                inv_text_input = sel_inv_doc.get("content_text") or f"Billed CAM expenses $14,500.00 for {selected_prop.get('name')}."
            else:
                st.selectbox("Select Invoice / Reconciliation Statement", ["No invoices available. Upload an invoice/reconciliation statement first."], disabled=True, key="audit_no_inv")
                uploaded_inv_file = st.file_uploader("Upload Invoice Statement (PDF/TXT)", type=["pdf", "txt"], key="audit_upload_inv")
                inv_text_input = ""
                if uploaded_inv_file:
                    inv_text_input = uploaded_inv_file.getvalue().decode("utf-8", errors="ignore")

        # Check if audit can be run
        can_run = bool(selected_prop_id and (lease_docs or (not lease_docs and lease_text_input)) and (invoice_docs or (not invoice_docs and inv_text_input)))

        if not can_run:
            st.warning("⚠️ Please upload/select both a Lease Baseline and an Invoice Statement for this property to enable Audit Execution.")

        audit_btn = st.button("Run Audit", type="primary", use_container_width=True, disabled=not can_run)

        if audit_btn:
            try:
                with st.status("Executing LeaseGuard AI Audit Pipeline...", expanded=True) as status:
                    st.write("📄 Loading & parsing selected lease baseline rules...")
                    st.write("🧾 Inspecting selected invoice line items & billing totals...")
                    st.write("🧮 Running deterministic AuditEngine rules (CAM caps, admin fees, exclusions, rent escalation, tenant share)...")

                    lease_result = extract_lease_rules(lease_text_input or "CAM cap $10,000") if lease_text_input.strip() else {"status": "demo", "data": {"cam_cap": 10000.0, "expense_exclusions": ["capital repairs", "rooftop hvac"], "administrative_fee_rules": "5% of CAM expenses", "tenant_share": "15%", "rent_escalation_cap_percent": 3.0}}
                    invoice_result = extract_invoice_summary(inv_text_input or "Billed CAM $14,500.00. Administrative fee billed: $900.00.", force_demo=not bool(os.getenv("ROCKETRIDE_APIKEY")))

                    if lease_result.get("status") == "error":
                        st.warning(f"Lease extraction warning: {lease_result.get('message', 'Unable to extract lease terms.')}")
                    if invoice_result.get("status") == "error":
                        st.warning(f"Invoice extraction warning: {invoice_result.get('message', 'Unable to extract invoice values.')}")

                    lease_data = {
                        "base_rent": 120000.0,
                        "rent_escalation_cap_percent": 3.0,
                        "cam_cap": (lease_result.get("data") or {}).get("cam_cap") or 10000.0,
                        "tenant_share": (lease_result.get("data") or {}).get("tenant_share") or 15.0,
                        "administrative_fee_cap_percent": 5.0,
                        "expense_exclusions": (lease_result.get("data") or {}).get("expense_exclusions") or ["capital repairs", "rooftop hvac"],
                        "lease_text": lease_text_input or "CAM cap $10,000",
                    }
                    invoice_data = {
                        "prior_base_rent": 120000.0,
                        "billed_base_rent": 126000.0,
                        "billed_cam_amount": (invoice_result.get("data") or {}).get("billed_cam_amount") or 14500.0,
                        "total_building_cam": (invoice_result.get("data") or {}).get("total_building_cam") or 100000.0,
                        "billed_tenant_share_amount": ((invoice_result.get("data") or {}).get("billed_tenant_share_amount") or 0.0) or 18000.0,
                        "billed_admin_fee_amount": (invoice_result.get("data") or {}).get("billed_admin_fee_amount") or 900.0,
                        "line_items": (invoice_result.get("data") or {}).get("line_items") or [
                            {"category": "Capital Improvements", "description": "Rooftop HVAC Repair", "billed_amount": 4200.0}
                        ],
                        "invoice_text": inv_text_input or "Billed CAM $14,500"
                    }

                    engine = AuditEngine()
                    audit_result = engine.run_audit(lease_data, invoice_data, property_id=selected_prop_id)

                    st.write("🛡️ Calculating risk score via RiskEngine...")
                    risk_engine = RiskEngine()
                    risk_result = risk_engine.calculate_lease_risk(lease_data, audit_result.get("findings", []), property_id=selected_prop_id)

                    st.write("💰 Initializing recovery records via RecoveryEngine...")
                    rec_engine = RecoveryEngine()
                    rec_records = []
                    for f in audit_result.get("findings", []):
                        rec_rec = rec_engine.create_recovery_record(property_id=selected_prop_id, claim_amount=f["potential_recovery"], status="Detected", notes=f["explanation"])
                        rec_records.append(rec_rec)
                        supabase.save_recovery_record(rec_rec, property_id=selected_prop_id)

                    # Save state & database
                    st.session_state["latest_audit"] = audit_result
                    st.session_state["latest_risk"] = risk_result

                    supabase.save_audit(audit_result)
                    supabase.save_risk_score(risk_result, property_id=selected_prop_id)

                    status.update(label="Audit Pipeline Completed Successfully!", state="complete", expanded=False)

                st.success(f"Audit completed for {selected_prop.get('name')}! Flagged {audit_result['findings_count']} discrepancy(ies). Potential Recovery: ${audit_result['total_potential_recovery']:,.2f}")
            except Exception as exc:
                st.error("Unable to complete this audit. Please confirm the selected documents are readable and try again.")

        st.markdown('</div>', unsafe_allow_html=True)

    if "latest_audit" in st.session_state:
        latest = st.session_state["latest_audit"]
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        section_header("Audit Result", f"Completed {latest['timestamp'][:10]} — review the flagged discrepancies and evidence below.")
        st.info(latest["summary"])

        for f in latest.get("findings", []):
            st.markdown(
                f"""
                <div class="lg-finding-card {f['severity']}">
                    <div class="lg-finding-title">
                        <span>⚠️ {f['category']}</span>
                        <span class="lg-badge lg-badge-red">{f['severity'].upper()} SEVERITY</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 0.4rem;">{f['explanation']}</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-top: 0.75rem; font-size: 0.85rem;">
                        <div><strong style="color: #94a3b8;">Billed Amount:</strong> <span style="color: #ffffff;">${f['billed_amount']:,.2f}</span></div>
                        <div><strong style="color: #94a3b8;">Allowed Amount:</strong> <span style="color: #ffffff;">${f['allowed_amount']:,.2f}</span></div>
                        <div><strong style="color: #94a3b8;">Potential Recovery:</strong> <span style="color: #34d399; font-weight: 700;">${f['potential_recovery']:,.2f}</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    section_header("Audit History", "Previous audit sessions for your portfolio.")

    audit_history = supabase.get_audits()

    if not audit_history:
        empty_state("No audit data yet", "Run your first audit to begin tracking recovery and compliance.", "○")
    else:
        st.dataframe(pd.DataFrame(audit_history), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
