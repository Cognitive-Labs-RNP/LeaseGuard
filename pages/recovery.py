"""
Financial Recovery Tracking Page for LeaseGuard AI (Phase 5 Cleanup).
Tracks overcharge recovery pipeline lifecycle from initial detection to landlord cash settlement using Supabase records.
"""

import streamlit as st
import pandas as pd
from services.auth import require_auth
from services.recovery_engine import RecoveryEngine, VALID_RECOVERY_STATUSES
from services.supabase import SupabaseService
from utils.ui import empty_state, page_header, section_header


def render():
    """Render Financial Recovery Pipeline view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Recovery", "Financial Recovery", "Track disputed funds from initial detection through review and recovered credit.")

    supabase = SupabaseService()
    recovery_records = supabase.get_recovery_records()

    rec_engine = RecoveryEngine()
    metrics = rec_engine.calculate_recovery_metrics(recovery_records)

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="lg-metric-card">
                <div class="lg-metric-label">1. Potential Identified</div>
                <div class="lg-metric-value">₹{metrics['potential_recovery']:,.2f}</div>
                <div class="lg-metric-trend lg-trend-neutral">Detected Claims</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="lg-metric-card warning">
                <div class="lg-metric-label">2. Disputed Amount</div>
                <div class="lg-metric-value">₹{metrics['disputed_amount']:,.2f}</div>
                <div class="lg-metric-trend lg-trend-neutral">Formal Notice Sent</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="lg-metric-card purple">
                <div class="lg-metric-label">3. Under Review</div>
                <div class="lg-metric-value">₹{metrics['amount_under_review']:,.2f}</div>
                <div class="lg-metric-trend lg-trend-neutral">In Negotiations</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="lg-metric-card success">
                <div class="lg-metric-label">4. Total Recovered</div>
                <div class="lg-metric-value">₹{metrics['recovered_amount']:,.2f}</div>
                <div class="lg-metric-trend lg-trend-up">Settled Credits</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    section_header("Recovery Pipeline", "Detected  →  Disputed  →  Under Review  →  Recovered")

    # Display stage columns (4 exact stages)
    stages = ["Detected", "Disputed", "Under Review", "Recovered"]
    scols = st.columns(len(stages))
    stage_colors = {"Detected": "#38bdf8", "Disputed": "#f59e0b", "Under Review": "#c084fc", "Recovered": "#10b981"}

    for idx, stage in enumerate(stages):
        stage_claims = [c for c in recovery_records if c.get("status") == stage]
        stage_sum = sum(float(c.get("claim_amount", 0.0)) for c in stage_claims)
        color = stage_colors[stage]

        with scols[idx]:
            st.markdown(
                f"""
                <div class="lg-card" style="padding: 0.85rem; border-top: 4px solid {color}; text-align: center;">
                    <div style="font-weight: 700; font-size: 0.9rem; color: #111827;">{stage}</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: {color}; margin: 0.35rem 0 0.2rem;">₹{stage_sum:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 600;">{len(stage_claims)} Active Claim(s)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    section_header("Recovery Claims", "Review individual claims and update their current lifecycle stage.")

    if not recovery_records:
        empty_state("No recovery claims yet", "Run an audit to identify overcharges and begin tracking recovery.", "○")
        return

    # Claim updater list
    for i, claim in enumerate(recovery_records):
        cid = claim.get("id", f"REC-{i}")
        cprop = claim.get("property_id", "Property")
        cnotes = claim.get("notes", "Discrepancy Claim")
        cclaim = float(claim.get("claim_amount", 0.0))
        cstatus = claim.get("status", "Detected")
        crecovered = float(claim.get("recovered_amount", 0.0))

        valid_list = sorted(list(VALID_RECOVERY_STATUSES))
        curr_idx = valid_list.index(cstatus) if cstatus in valid_list else 0

        with st.expander(f"📌 {cid} - {cprop} ({cnotes[:30]}) - ₹{cclaim:,.2f}"):
            ucol1, ucol2, ucol3 = st.columns(3)
            with ucol1:
                st.write(f"**Dispute Notes:** {cnotes}")
                st.write(f"**Current Status:** `{cstatus}`")
            with ucol2:
                new_status = st.selectbox("Update Status", valid_list, index=curr_idx, key=f"rec_stat_{i}")
            with ucol3:
                rec_amt_input = st.number_input("Settled Amount (₹)", value=crecovered, step=100.0, key=f"rec_amt_{i}")
                if st.button("Save Updates", key=f"rec_save_{i}"):
                    supabase.update_recovery_status(cid, new_status, rec_amt_input)
                    st.success(f"Claim {cid} updated to '{new_status}'!")
                    st.rerun()


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
