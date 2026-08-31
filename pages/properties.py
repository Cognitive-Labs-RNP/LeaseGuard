"""
Properties Page for LeaseGuard AI (Phase 5 Cleanup).
Property portfolio management and detailed single-property audit overview using Supabase records.
"""

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
    """Render Property Portfolio & Detail view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Portfolio", "Properties", "Inspect lease compliance, risk exposure, documents, and recovery at the property level.")

    supabase = SupabaseService()
    properties = supabase.get_properties()

    # Form to add a new property
    with st.expander("➕ Add New Commercial Property"):
        with st.form("add_property_form"):
            col1, col2 = st.columns(2)
            with col1:
                p_name = st.text_input("Property Name", placeholder="e.g. Skyline Commercial Center")
                p_code = st.text_input("Property Code", placeholder="e.g. PROP-001")
            with col2:
                p_address = st.text_input("Address", placeholder="e.g. 100 Financial Plaza, Suite 400")
                p_sqft = st.number_input("Square Footage (sq ft)", min_value=0, value=25000, step=1000)

            create_submit = st.form_submit_button("Save Property", type="primary", use_container_width=True)
            if create_submit:
                if not p_name or not p_name.strip():
                    st.error("Property name is required.")
                else:
                    try:
                        new_prop_payload = {
                            "name": p_name.strip(),
                            "property_code": (p_code or "").strip() or f"PROP-{len(properties)+1:03d}",
                            "address": (p_address or "").strip() or "N/A",
                            "square_footage": float(p_sqft),
                            "status": "Active"
                        }
                        saved = supabase.create_property(new_prop_payload)
                        if saved:
                            st.success(f"Property '{p_name}' added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add property. Database record creation was unsuccessful.")
                    except Exception as exc:
                        st.error(f"Failed to add property: {str(exc)}")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    if not properties:
        st.info("No properties added yet. Use the form above to add your first commercial building property.")
        return

    prop_map = {f"{p.get('code', 'PROP')}: {p.get('name')}": p for p in properties}
    section_header("Property Overview", "Choose a property to review its audit and recovery profile.")
    selected_prop_label = st.selectbox("Property", list(prop_map.keys()))
    prop = prop_map[selected_prop_label]
    prop_id = prop.get("id")

    # Fetch property related records from Supabase
    prop_docs = supabase.get_documents(property_id=prop_id)
    prop_audits = supabase.get_audits(property_id=prop_id)
    prop_findings = supabase.get_findings(property_id=prop_id)
    prop_risks = supabase.get_risk_scores(property_id=prop_id)
    prop_recoveries = supabase.get_recovery_records(property_id=prop_id)

    latest_risk = prop_risks[-1].get("score", 0) if prop_risks else 0
    risk_tier = "High Risk" if latest_risk >= 70 else ("Moderate Risk" if latest_risk >= 30 else "Low Risk")

    pot_rec = sum(float(f.get("amount", 0.0)) for f in prop_findings)
    rec_amt = sum(float(r.get("recovered_amount", 0.0)) for r in prop_recoveries)

    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    with pcol1:
        st.markdown(
            f"""
            <div class="lg-metric-card">
                <div class="lg-metric-label">Square Footage</div>
                <div class="lg-metric-value">{int(prop.get('square_feet', 0)):,} sq ft</div>
                <div class="lg-metric-trend lg-trend-neutral">{prop.get('status', 'Active')} Lease</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with pcol2:
        badge_cls = "danger" if latest_risk >= 70 else ("warning" if latest_risk >= 30 else "success")
        st.markdown(
            f"""
            <div class="lg-metric-card {badge_cls}">
                <div class="lg-metric-label">Risk Rating Score</div>
                <div class="lg-metric-value">{latest_risk} / 100</div>
                <div class="lg-metric-trend lg-trend-neutral">{risk_tier}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with pcol3:
        st.markdown(
            f"""
            <div class="lg-metric-card warning">
                <div class="lg-metric-label">Potential Recovery</div>
                <div class="lg-metric-value">${pot_rec:,.2f}</div>
                <div class="lg-metric-trend lg-trend-neutral">{len(prop_findings)} Findings Flagged</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with pcol4:
        st.markdown(
            f"""
            <div class="lg-metric-card success">
                <div class="lg-metric-label">Recovered Amount</div>
                <div class="lg-metric-value">${rec_amt:,.2f}</div>
                <div class="lg-metric-trend lg-trend-up">Credited to Rent</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Tabs for Property Detail
    tab_info, tab_docs, tab_audits, tab_findings, tab_recovery, tab_perf = st.tabs([
        "ℹ️ Info & Risk", "📁 Documents", "🔍 Audits", "⚠️ Findings", "💰 Recovery", "📈 Historical Performance"
    ])

    with tab_info:
        st.markdown("### 📌 Property Information")
        st.write(f"**Name:** {prop.get('name')}")
        st.write(f"**Address:** {prop.get('address', 'N/A')}")
        st.write(f"**Code:** `{prop.get('code')}`")
        st.markdown("#### 🛡️ Risk Summary")
        if prop_risks:
            st.info(prop_risks[-1].get("summary", "Risk assessment active."))
        else:
            st.caption("No risk assessment conducted yet for this property.")

    with tab_docs:
        st.markdown("### 📁 Associated Documents")
        if prop_docs:
            st.dataframe(pd.DataFrame(prop_docs), use_container_width=True, hide_index=True)
        else:
            empty_state("No documents yet", "Upload a lease or billing document for this property to begin an audit.", "□")

    with tab_audits:
        st.markdown("### 🔍 Historical Audit Sessions")
        if prop_audits:
            st.dataframe(pd.DataFrame(prop_audits), use_container_width=True, hide_index=True)
        else:
            empty_state("No audit data yet", "Run an audit for this property to begin measuring lease compliance.", "○")

    with tab_findings:
        st.markdown("### ⚠️ Property Discrepancies & Findings")
        if prop_findings:
            st.dataframe(pd.DataFrame(prop_findings), use_container_width=True, hide_index=True)
        else:
            empty_state("No findings detected", "Completed audits with violations will appear here.", "✓")

    with tab_recovery:
        st.markdown("### 💰 Financial Recovery Progress")
        ratio = min(1.0, rec_amt / max(1.0, pot_rec)) if pot_rec > 0 else 0.0
        st.progress(ratio)
        st.write(f"**Recovered:** ${rec_amt:,.2f} of ${pot_rec:,.2f} identified")

    with tab_perf:
        st.markdown("### 📈 Property Risk Trend")
        if len(prop_risks) > 1:
            dates = [r.get("created_at", "")[:10] for r in prop_risks]
            scores = [float(r.get("score", 0)) for r in prop_risks]
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', name='Risk Score', line=dict(color='#f43f5e', width=3)))
            fig_trend.update_layout(**_get_plotly_layout_defaults(), title="Historical Risk Score Trend", height=280)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            empty_state("No historical trend yet", "Risk history appears after multiple audits for this property.", "↗")


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
