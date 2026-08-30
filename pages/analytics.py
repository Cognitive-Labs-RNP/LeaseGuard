"""
Portfolio Analytics Page for LeaseGuard AI.
Visualizes cross-property performance, historical overcharge trends, and audit benchmarks.
"""
import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    """Render Analytics and Reporting view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">📈 Cross-Property Analytics & Trends</div>
            <div class="lg-subtitle">Compare multi-property billing variances, landlord dispute track records, and historical recovery.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Identified Overcharges by Category")
        category_df = pd.DataFrame({
            "Category": ["CAM Cap Violations", "Capital Exclusions", "Pro-Rata Errors", "Management Fee Markups", "Utility Allocation"],
            "Amount": [72000, 48500, 31200, 18400, 14150]
        })
        fig_cat = px.bar(
            category_df,
            x="Category",
            y="Amount",
            text="Amount",
            color="Category",
            color_discrete_sequence=["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
        )
        fig_cat.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            height=320,
            xaxis_title="",
            yaxis_title="Variance ($)"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with chart_col2:
        st.markdown("#### Historical Recovery Rate (2025 - 2026)")
        trend_df = pd.DataFrame({
            "Quarter": ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", "Q1 2026", "Q2 2026"],
            "Recovered ($)": [18000, 24500, 38000, 42000, 56000, 62400]
        })
        fig_trend = px.line(
            trend_df,
            x="Quarter",
            y="Recovered ($)",
            markers=True,
            line_shape="spline"
        )
        fig_trend.update_traces(line_color="#10b981", line_width=3)
        fig_trend.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=320,
            xaxis_title="",
            yaxis_title="Total Recovered ($)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("### 🏢 Landlord Compliance Scorecard")
    landlords_df = pd.DataFrame([
        {
            "Landlord / Mgmt Co.": "Horizon Properties LLC",
            "Properties Managed": 4,
            "Total Invoiced (2025)": "$620,000",
            "Disputed Overcharges": "$44,800",
            "Variance %": "7.2%",
            "Dispute Settlement Avg": "18 days"
        },
        {
            "Landlord / Mgmt Co.": "Apex Industrial Holdings",
            "Properties Managed": 2,
            "Total Invoiced (2025)": "$340,000",
            "Disputed Overcharges": "$0.00",
            "Variance %": "0.0%",
            "Dispute Settlement Avg": "N/A"
        },
        {
            "Landlord / Mgmt Co.": "Beacon Asset Management",
            "Properties Managed": 5,
            "Total Invoiced (2025)": "$890,000",
            "Disputed Overcharges": "$82,300",
            "Variance %": "9.2%",
            "Dispute Settlement Avg": "34 days"
        }
    ])
    st.dataframe(landlords_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
