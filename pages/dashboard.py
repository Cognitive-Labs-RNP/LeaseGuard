"""
Dashboard Page for LeaseGuard AI (Phase 5 Cleanup).
Enterprise SaaS Overview Dashboard connected dynamically to Supabase records with zero-state support.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.auth import require_auth
from services.supabase import SupabaseService
from utils.ui import empty_state, metric_card, page_header, section_header


def _get_plotly_layout_defaults():
    """Return dark indie-premium theme styling defaults for Plotly charts."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True),
    )


def render():
    """Render main SaaS portfolio dashboard."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("LeaseGuard", "Portfolio Intelligence", "Monitor billing risk, recoverable spend, and lease compliance across your portfolio.")

    # Show demo banner if user is demo account
    if user.get("email") == "demo@leaseguard.ai":
        st.info(
            "🎯 **You are exploring the LeaseGuard demo workspace.** "
            "This is a read-only demonstration with sample data. "
            "[Sign in with your own account](/) to audit your real properties.",
            icon="✨"
        )

    supabase = SupabaseService()
    properties = supabase.get_properties()
    audits = supabase.get_audits()
    findings = supabase.get_findings()
    risk_scores = supabase.get_risk_scores()
    recovery_records = supabase.get_recovery_records()

    # Calculate real KPI metrics
    total_properties = len(properties)
    total_audits = len(audits)
    total_findings = len(findings)

    potential_rec = sum(float(f.get("amount", 0.0)) for f in findings)
    if not potential_rec and recovery_records:
        potential_rec = sum(float(r.get("claim_amount", 0.0)) for r in recovery_records)

    recovered_amt = sum(float(r.get("recovered_amount", 0.0)) for r in recovery_records)

    if risk_scores:
        scores_list = [float(rs.get("score", 0)) for rs in risk_scores]
        avg_risk = round(sum(scores_list) / len(scores_list), 1)
        high_risk_cnt = sum(1 for s in scores_list if s >= 70)
        med_risk_cnt = sum(1 for s in scores_list if 30 <= s < 70)
        low_risk_cnt = sum(1 for s in scores_list if s < 30)
    else:
        avg_risk, high_risk_cnt, med_risk_cnt, low_risk_cnt = 0.0, 0, 0, 0

    # -------------------------------------------------------------------------
    # 1. Portfolio KPIs
    # -------------------------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Total Properties", str(total_properties), "Portfolio assets", "")
    with col2:
        metric_card("Active Audits", str(total_audits), "Completed audit sessions", "purple")
    with col3:
        metric_card("Potential Recovery", f"${potential_rec:,.2f}", f"{total_findings} flagged findings", "warning")
    with col4:
        metric_card("Recovered Amount", f"${recovered_amt:,.2f}", "Settled credits", "success")
    with col5:
        metric_card("Portfolio Risk", f"{avg_risk:g} / 100" if risk_scores else "Unassessed", "Latest portfolio assessment", "danger" if avg_risk >= 70 else "warning")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Portfolio Risk & Recovery Tracking Summary Row
    # -------------------------------------------------------------------------
    rcol1, rcol2 = st.columns([1, 1])

    risk_badge = "High Exposure" if avg_risk >= 70 else ("Moderate Exposure" if avg_risk >= 30 else "Low Risk")
    risk_color_cls = "lg-badge-red" if avg_risk >= 70 else ("lg-badge-amber" if avg_risk >= 30 else "lg-badge-green")

    with rcol1:
        st.markdown(
            f"""
            <div class="lg-card">
                <div style="font-weight: 700; font-size: 1.1rem; color: #ffffff; margin-bottom: 0.75rem;">
                    🛡️ Portfolio Risk Breakdown
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">Average Portfolio Score</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: #fbbf24;">{avg_risk if risk_scores else '0'} <span style="font-size: 1rem; color: #64748b;">/ 100</span></div>
                    </div>
                    <div>
                        <span class="lg-badge {risk_color_cls}">{risk_badge if risk_scores else 'Unassessed'}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; text-align: center;">
                    <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.2); padding: 0.5rem; border-radius: 8px;">
                        <div style="font-size: 1.2rem; font-weight: 800; color: #f87171;">{high_risk_cnt}</div>
                        <div style="font-size: 0.72rem; color: #94a3b8;">High Risk</div>
                    </div>
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); padding: 0.5rem; border-radius: 8px;">
                        <div style="font-size: 1.2rem; font-weight: 800; color: #fbbf24;">{med_risk_cnt}</div>
                        <div style="font-size: 0.72rem; color: #94a3b8;">Medium Risk</div>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 0.5rem; border-radius: 8px;">
                        <div style="font-size: 1.2rem; font-weight: 800; color: #34d399;">{low_risk_cnt}</div>
                        <div style="font-size: 0.72rem; color: #94a3b8;">Low Risk</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Compute recovery pipeline amounts
    rec_potential = sum(float(r.get("claim_amount", 0)) for r in recovery_records if r.get("status") == "Detected")
    rec_disputed = sum(float(r.get("claim_amount", 0)) for r in recovery_records if r.get("status") == "Disputed")
    rec_review = sum(float(r.get("claim_amount", 0)) for r in recovery_records if r.get("status") == "Under Review")
    rec_settled = sum(float(r.get("recovered_amount", 0)) for r in recovery_records if r.get("status") == "Recovered")

    with rcol2:
        st.markdown(
            f"""
            <div class="lg-card">
                <div style="font-weight: 700; font-size: 1.1rem; color: #ffffff; margin-bottom: 0.75rem;">
                    💰 Recovery Pipeline Status
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                    <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); padding: 0.75rem; border-radius: 8px;">
                        <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">POTENTIAL</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #38bdf8;">${rec_potential:,.2f}</div>
                    </div>
                    <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.2); padding: 0.75rem; border-radius: 8px;">
                        <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">DISPUTED</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #fbbf24;">${rec_disputed:,.2f}</div>
                    </div>
                    <div style="background: rgba(192, 132, 252, 0.08); border: 1px solid rgba(192, 132, 252, 0.2); padding: 0.75rem; border-radius: 8px;">
                        <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">UNDER REVIEW</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #c084fc;">${rec_review:,.2f}</div>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); padding: 0.75rem; border-radius: 8px;">
                        <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">RECOVERED</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #34d399;">${rec_settled:,.2f}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # 3. Interactive Charts (Historical Recovery & Findings by Category)
    # -------------------------------------------------------------------------
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    ccol1, ccol2 = st.columns(2)

    with ccol1:
        st.markdown("### 📈 Historical Recovery Trend")
        if recovery_records:
            dates = [r.get("created_at", "")[:10] for r in recovery_records]
            claims = [float(r.get("claim_amount", 0)) for r in recovery_records]
            settled = [float(r.get("recovered_amount", 0)) for r in recovery_records]
            history_df = pd.DataFrame({"Date": dates, "Identified": claims, "Recovered": settled})
            fig_rec = go.Figure()
            fig_rec.add_trace(go.Scatter(
                x=history_df["Date"], y=history_df["Identified"],
                mode='lines+markers', name='Identified Overcharges',
                line=dict(color='#38bdf8', width=3),
                fill='tonexty', fillcolor='rgba(56, 189, 248, 0.1)'
            ))
            fig_rec.add_trace(go.Scatter(
                x=history_df["Date"], y=history_df["Recovered"],
                mode='lines+markers', name='Recovered Cash/Credit',
                line=dict(color='#10b981', width=3),
                fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.15)'
            ))
            fig_rec.update_layout(**_get_plotly_layout_defaults(), title="Cumulative Recovery vs Identified ($)", height=280)
            st.plotly_chart(fig_rec, use_container_width=True)
        else:
            st.info("No recovery history available yet. Run an audit to identify recoverable lease overcharges.")

    with ccol2:
        st.markdown("### 🏷️ Findings by Category")
        if findings:
            cat_counts = {}
            for f in findings:
                cat = f.get("finding_type") or f.get("category") or "Other"
                amt = float(f.get("amount") or f.get("potential_recovery") or 0.0)
                cat_counts[cat] = cat_counts.get(cat, 0.0) + amt

            cat_df = pd.DataFrame([{"Category": k, "Overcharge": v} for k, v in cat_counts.items()])
            fig_cat = px.pie(
                cat_df, values="Overcharge", names="Category",
                color_discrete_sequence=["#38bdf8", "#818cf8", "#f59e0b", "#f43f5e", "#c084fc"],
                hole=0.45
            )
            fig_cat.update_layout(**_get_plotly_layout_defaults(), title="Potential Recovery Distribution ($)", height=280)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No findings available yet. Upload leases and invoices to launch your first audit.")

    # -------------------------------------------------------------------------
    # 4. High-Risk Properties, Recent Findings & Action Required Row
    # -------------------------------------------------------------------------
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    tcol1, tcol2 = st.columns([1.1, 0.9])

    with tcol1:
        st.markdown("### 🏢 High-Risk Properties")
        if properties:
            risk_table_rows = []
            for p in properties:
                pid = p.get("id")
                pname = p.get("name", "Unknown Property")
                pfindings = [f for f in findings if f.get("property_id") == pid]
                prisk = [r for r in risk_scores if r.get("property_id") == pid]
                rscore = prisk[0].get("score", 0) if prisk else 0
                rtier = "HIGH" if rscore >= 70 else ("MEDIUM" if rscore >= 30 else "LOW")
                p_rec = sum(float(f.get("amount", 0)) for f in pfindings)
                risk_table_rows.append({
                    "Property": pname,
                    "Risk Score": f"{rscore} / 100",
                    "Risk Tier": rtier,
                    "Findings": len(pfindings),
                    "Potential Recovery": f"${p_rec:,.2f}"
                })
            st.dataframe(pd.DataFrame(risk_table_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No properties added yet. Add properties in the Properties or Audits module.")

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### ⚠️ Recent Discrepancy Findings")
        if findings:
            for rf in findings[:3]:
                sev_badge = "lg-badge-red" if rf.get("severity") == "high" else "lg-badge-amber"
                st.markdown(
                    f"""
                    <div class="lg-card" style="padding: 0.85rem 1.1rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-weight: 700; color: #ffffff; font-size: 0.9rem;">⚠️ {rf.get('title') or rf.get('finding_type')}</div>
                            <div>
                                <span class="lg-badge {sev_badge}">{(rf.get('severity') or 'medium').upper()}</span>
                                <span class="lg-badge lg-badge-gray">{rf.get('status', 'Open')}</span>
                            </div>
                        </div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem;">
                            Potential Recovery: <strong style="color: #34d399;">${float(rf.get('amount', 0)):,.2f}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No findings recorded yet.")

    with tcol2:
        st.markdown("### ⚡ Action Required")
        if total_properties == 0:
            st.markdown(
                """
                <div class="lg-card" style="padding: 0.9rem 1.1rem; border-left: 4px solid #38bdf8; margin-bottom: 0.6rem;">
                    <div style="font-weight: 700; color: #ffffff; font-size: 0.9rem;">Add Your First Property</div>
                    <div style="font-size: 0.78rem; color: #94a3b8;">Create property records to begin tracking commercial lease audits.</div>
                    <div style="margin-top: 0.4rem;"><span class="lg-badge lg-badge-blue">Getting Started</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif total_audits == 0:
            st.markdown(
                """
                <div class="lg-card" style="padding: 0.9rem 1.1rem; border-left: 4px solid #f59e0b; margin-bottom: 0.6rem;">
                    <div style="font-weight: 700; color: #ffffff; font-size: 0.9rem;">Run Initial Lease Audit</div>
                    <div style="font-size: 0.78rem; color: #94a3b8;">Upload your lease contract and annual CAM statement to audit overcharges.</div>
                    <div style="margin-top: 0.4rem;"><span class="lg-badge lg-badge-amber">Audit Recommended</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="lg-card" style="padding: 0.9rem 1.1rem; border-left: 4px solid #10b981; margin-bottom: 0.6rem;">
                    <div style="font-weight: 700; color: #ffffff; font-size: 0.9rem;">All Audits Up To Date</div>
                    <div style="font-size: 0.78rem; color: #94a3b8;">No pending action items for active property portfolio.</div>
                    <div style="margin-top: 0.4rem;"><span class="lg-badge lg-badge-green">Optimal Status</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
