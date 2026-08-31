"""
Analytics & Trends Page for LeaseGuard AI (Phase 5 Cleanup).
Interactive multi-property comparison analytics and historical trend charts powered by Plotly and Supabase data.
"""

import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.auth import require_auth
from services.supabase import SupabaseService
from utils.ui import empty_state, page_header, section_header


def _get_plotly_layout_defaults():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True),
    )


def render():
    """Render Portfolio Analytics view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Insights", "Portfolio Analytics", "Compare recovery, findings, and risk performance across time and properties.")

    supabase = SupabaseService()
    properties = supabase.get_properties()
    findings = supabase.get_findings()
    risk_scores = supabase.get_risk_scores()
    recovery_records = supabase.get_recovery_records()

    tab1, tab2 = st.tabs(["📉 Historical Comparison", "🏢 Multiple-Property Analytics"])

    # -------------------------------------------------------------------------
    # Tab 1: Historical Comparison
    # -------------------------------------------------------------------------
    with tab1:
        section_header("Historical Comparison", "Compare one property's performance over time.")
        if not properties:
            empty_state("No historical data yet", "Add properties and conduct audits to begin tracking performance over time.", "○")
        else:
            hcol1, hcol2, hcol3 = st.columns(3)

            with hcol1:
                prop_map = {p.get("name"): p for p in properties}
                sel_hist_prop = st.selectbox("Select Target Property", list(prop_map.keys()))
            with hcol2:
                sel_metric = st.selectbox(
                    "Select Metric to Track",
                    ["Risk Score", "Findings", "Potential Recovery", "Recovered Amount"]
                )
            with hcol3:
                date_range = st.date_input(
                    "Date Range",
                    value=[datetime.date(2025, 1, 1), datetime.date(2026, 8, 31)]
                )

            target_p = prop_map[sel_hist_prop]
            pid = target_p.get("id")
            p_risks = [r for r in risk_scores if r.get("property_id") == pid]
            p_findings = [f for f in findings if f.get("property_id") == pid]
            p_recs = [r for r in recovery_records if r.get("property_id") == pid]

            if sel_metric == "Risk Score" and p_risks:
                dates = [r.get("created_at", "")[:10] for r in p_risks]
                vals = [float(r.get("score", 0)) for r in p_risks]
            elif sel_metric == "Findings" and p_findings:
                dates = [f.get("created_at", "")[:10] for f in p_findings]
                vals = [1 for _ in p_findings]
            elif sel_metric == "Potential Recovery" and p_findings:
                dates = [f.get("created_at", "")[:10] for f in p_findings]
                vals = [float(f.get("amount", 0)) for f in p_findings]
            elif sel_metric == "Recovered Amount" and p_recs:
                dates = [r.get("created_at", "")[:10] for r in p_recs]
                vals = [float(r.get("recovered_amount", 0)) for r in p_recs]
            else:
                dates, vals = [], []

            if dates and vals:
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Scatter(
                    x=dates, y=vals, mode='lines+markers', name=f"{sel_hist_prop} - {sel_metric}",
                    line=dict(color='#38bdf8', width=3), fill='tozeroy', fillcolor="rgba(56, 189, 248, 0.1)"
                ))
                fig_hist.update_layout(**_get_plotly_layout_defaults(), title=f"Historical {sel_metric} Trend for {sel_hist_prop}", height=340)
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                empty_state("No trend data for this selection", "Choose another metric or run additional audits for this property.", "○")

    # -------------------------------------------------------------------------
    # Tab 2: Multiple-Property Analytics
    # -------------------------------------------------------------------------
    with tab2:
        section_header("Multi-Property Analytics", "Compare portfolio properties against each other.")
        if not properties:
            empty_state("No properties to compare", "Add properties and audit records to build a portfolio comparison.", "○")
        else:
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                sel_compare_metric = st.selectbox(
                    "Comparison Metric",
                    ["Risk Score", "Findings", "Potential Recovery", "Recovered Amount"]
                )
            with mcol2:
                st.write("")

            prop_matrix = []
            for p in properties:
                pid = p.get("id")
                p_f = [f for f in findings if f.get("property_id") == pid]
                p_r = [r for r in risk_scores if r.get("property_id") == pid]
                p_rec = [r for r in recovery_records if r.get("property_id") == pid]

                r_score = p_r[-1].get("score", 0) if p_r else 0
                pot_val = sum(float(f.get("amount", 0)) for f in p_f)
                rec_val = sum(float(r.get("recovered_amount", 0)) for r in p_rec)

                prop_matrix.append({
                    "Property": p.get("name", "Unknown"),
                    "Risk Score": r_score,
                    "Findings": len(p_f),
                    "Potential Recovery": pot_val,
                    "Recovered Amount": rec_val,
                    "SqFt": int(p.get("square_feet", 0))
                })

            df_all = pd.DataFrame(prop_matrix)

            fig_comp = px.bar(
                df_all, x="Property", y=sel_compare_metric,
                color=sel_compare_metric,
                color_continuous_scale=["#10b981", "#fbbf24", "#f43f5e"] if sel_compare_metric == "Risk Score" else ["#38bdf8", "#818cf8", "#c084fc"]
            )
            fig_comp.update_layout(**_get_plotly_layout_defaults(), title=f"Property Comparison by {sel_compare_metric}", height=340)
            st.plotly_chart(fig_comp, use_container_width=True)

            st.markdown("### 📋 Multi-Property Summary Matrix")
            formatted_df = df_all.copy()
            formatted_df["Potential Recovery"] = formatted_df["Potential Recovery"].apply(lambda x: f"${x:,.2f}")
            formatted_df["Recovered Amount"] = formatted_df["Recovered Amount"].apply(lambda x: f"${x:,.2f}")
            formatted_df["SqFt"] = formatted_df["SqFt"].apply(lambda x: f"{x:,} sq ft")
            st.dataframe(formatted_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
