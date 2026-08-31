"""
Risk Analysis Page for LeaseGuard AI (Phase 5 Cleanup).
Evaluates lease contract ambiguity, risk scores (0-100), category vulnerability radar charts, and exposure ratings using Supabase data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.auth import require_auth
from services.supabase import SupabaseService
from utils.ui import empty_state, metric_card, page_header, section_header


def _get_plotly_layout_defaults():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", family="Plus Jakarta Sans", size=12),
        title_font=dict(color="#111827", family="Plus Jakarta Sans", size=14),
        legend=dict(font=dict(color="#111827"), bgcolor="#FFFFFF", bordercolor="#F3E1CB", borderwidth=1),
        margin=dict(l=20, r=20, t=30, b=20),
    )


def render():
    """Render Risk Analysis view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Audit", "Risk Analysis", "Quantitative exposure scoring across CAM, escalations, administrative fees, tax, and audit rights.")

    supabase = SupabaseService()
    risk_scores = supabase.get_risk_scores()
    properties = supabase.get_properties()

    if risk_scores:
        scores_list = [float(rs.get("score", 0)) for rs in risk_scores]
        avg_score = round(sum(scores_list) / len(scores_list), 1)
        high_cnt = sum(1 for s in scores_list if s >= 70)
        avg_str = f"{avg_score} / 100"
        high_str = f"{high_cnt} Contracts"
        rate_str = f"{round((len(risk_scores) / max(1, len(properties))) * 100, 1)}%"
    else:
        avg_str = "0 / 100"
        high_str = "0 Contracts"
        rate_str = "0%"

    rcol1, rcol2, rcol3 = st.columns(3)
    with rcol1:
        st.markdown(
            f"""
            <div class="lg-metric-card warning">
                <div class="lg-metric-label">Average Portfolio Risk</div>
                <div class="lg-metric-value">{avg_str}</div>
                <div class="lg-metric-trend lg-trend-neutral">Portfolio Exposure</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rcol2:
        st.markdown(
            f"""
            <div class="lg-metric-card danger">
                <div class="lg-metric-label">High-Risk Contracts</div>
                <div class="lg-metric-value">{high_str}</div>
                <div class="lg-metric-trend lg-trend-down">Score >= 70</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rcol3:
        st.markdown(
            f"""
            <div class="lg-metric-card success">
                <div class="lg-metric-label">Audited Safeguard Rate</div>
                <div class="lg-metric-value">{rate_str}</div>
                <div class="lg-metric-trend lg-trend-up">Coverage across portfolio</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if not risk_scores:
        empty_state("No risk assessments yet", "Run an audit to calculate lease risk ratings for this portfolio.", "○")
        return

    # Risk Radar & Bar Chart Row
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        section_header("Risk Category Breakdown", "Lease-vulnerability signals assessed by the existing risk engine.")
        category_scores = risk_scores[-1].get("category_scores") if risk_scores else None
        if isinstance(category_scores, dict) and category_scores:
            categories = [key.replace("_", " ").title() for key in category_scores]
            scores_active = [float(value) for value in category_scores.values()]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=scores_active, theta=categories, fill='toself', name='Lease Risk Profile',
                line=dict(color='#f43f5e', width=2)
            ))
            fig_radar.update_layout(**_get_plotly_layout_defaults(), polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E8D5BD"), angularaxis=dict(gridcolor="#E8D5BD")), height=360, showlegend=False)
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            empty_state("Category detail unavailable", "Risk category detail is shown when it is available in the saved assessment.", "○")

    with col_chart2:
        section_header("Property Risk Scorecard", "Latest risk scores across audited properties.")
        risk_df = pd.DataFrame([
            {"Property": rs.get("property_id", "Property"), "Score": float(rs.get("score", 0)), "Tier": rs.get("risk_level", "Moderate")}
            for rs in risk_scores
        ])
        fig_bar = px.bar(
            risk_df, x="Score", y="Property", orientation="h",
            color="Score", color_continuous_scale=["#10b981", "#fbbf24", "#f43f5e"]
        )
        fig_bar.update_layout(**_get_plotly_layout_defaults(), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)

    section_header("Risk Diagnostics", "Source risk records used in the portfolio score.")
    st.dataframe(pd.DataFrame(risk_scores), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
