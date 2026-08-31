"""
Findings & Overcharges Page for LeaseGuard AI (Phase 5 Cleanup).
Inspect, filter, and take action on identified lease overcharge findings from Supabase.
"""

import streamlit as st
import pandas as pd
from services.auth import require_auth
from services.supabase import SupabaseService
from utils.ui import empty_state, page_header, section_header


def render():
    """Render Discrepancy Findings & Overcharges view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Audit", "Findings", "Review flagged discrepancies, supporting evidence, and potential recovery.")

    supabase = SupabaseService()
    findings_data = supabase.get_findings()

    if not findings_data:
        empty_state("No findings detected", "Completed audits with violations will appear here.", "✓")
        return

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------
    section_header("Filter Findings", "Narrow the findings list by property, severity, category, or recovery status.")
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)

    properties_list = ["All Properties"] + list(set(f.get("property_id", "Unknown") for f in findings_data))
    severities_list = ["All Severities", "high", "medium", "low"]
    categories_list = ["All Categories"] + list(set(f.get("finding_type", "Discrepancy") for f in findings_data))
    statuses_list = ["All Statuses", "open", "Disputed", "Under Review", "Recovered"]

    with fcol1:
        sel_prop = st.selectbox("Property", properties_list)
    with fcol2:
        sel_sev = st.selectbox("Severity", severities_list)
    with fcol3:
        sel_cat = st.selectbox("Category", categories_list)
    with fcol4:
        sel_stat = st.selectbox("Status", statuses_list)

    # Filter logic
    filtered = findings_data
    if sel_prop != "All Properties":
        filtered = [f for f in filtered if f.get("property_id") == sel_prop]
    if sel_sev != "All Severities":
        filtered = [f for f in filtered if f.get("severity") == sel_sev]
    if sel_cat != "All Categories":
        filtered = [f for f in filtered if f.get("finding_type") == sel_cat]
    if sel_stat != "All Statuses":
        filtered = [f for f in filtered if f.get("status") == sel_stat]

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"### 📋 Discrepancies Flagged ({len(filtered)})")

    if not filtered:
        empty_state("No matching findings", "Adjust the active filters to review another set of results.", "○")
        return

    for idx, f in enumerate(filtered):
        sev = f.get("severity", "medium")
        sev_color = "red" if sev == "high" else ("amber" if sev == "medium" else "blue")
        stat = f.get("status", "open")
        stat_color = "green" if stat == "Recovered" else ("purple" if stat == "Under Review" else "amber")
        amt = float(f.get("amount", 0.0))
        billed = float(f.get("billed_amount", amt))
        allowed = float(f.get("allowed_amount", 0.0))

        with st.container():
            st.markdown(
                f"""
                <div class="lg-finding-card {sev}">
                    <div class="lg-finding-title">
                        <span>⚠️ {f.get('title') or f.get('finding_type')} <span style="font-size: 0.85rem; color: #94a3b8; font-weight: 500;">({f.get('property_id', 'Property')})</span></span>
                        <div>
                            <span class="lg-badge lg-badge-{sev_color}">{sev.upper()}</span>
                            <span class="lg-badge lg-badge-{stat_color}">{stat}</span>
                        </div>
                    </div>
                    <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 0.5rem;">{f.get('description', '')}</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-top: 0.75rem; font-size: 0.85rem;">
                        <div><strong style="color: #94a3b8;">Billed:</strong> <span style="color: #ffffff;">${billed:,.2f}</span></div>
                        <div><strong style="color: #94a3b8;">Allowed:</strong> <span style="color: #ffffff;">${allowed:,.2f}</span></div>
                        <div><strong style="color: #94a3b8;">Potential Recovery:</strong> <span style="color: #34d399; font-weight: 700;">${amt:,.2f}</span></div>
                    </div>
                    <div class="lg-evidence-box"><strong>Why this was flagged</strong><br>{f.get('description') or 'The billed amount did not align with the lease terms evaluated during the audit.'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            col_act1, col_act2 = st.columns([0.3, 0.7])
            with col_act1:
                if st.button(f"✉️ Generate Dispute Letter", key=f"btn_{f.get('id', idx)}"):
                    st.session_state["target_dispute_finding"] = f
                    st.info(f"Selected finding '{f.get('title')}' for dispute letter generation. Go to ✉️ Disputes page to review.")


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
