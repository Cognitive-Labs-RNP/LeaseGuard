"""Small, reusable presentation helpers for the LeaseGuard Streamlit UI."""

from __future__ import annotations

from html import escape
from typing import Optional

import streamlit as st


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    """Render the shared page title treatment without duplicating markup."""
    st.markdown(
        f"""
        <div class="lg-page-header">
            <div class="lg-eyebrow">{escape(eyebrow)}</div>
            <div class="lg-title">{escape(title)}</div>
            <div class="lg-subtitle">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, description: Optional[str] = None) -> None:
    """Render a consistent section heading and optional supporting copy."""
    description_html = f'<div class="lg-section-description">{escape(description)}</div>' if description else ""
    st.markdown(
        f'<div class="lg-section-header"><div class="lg-section-title">{escape(title)}</div>{description_html}</div>',
        unsafe_allow_html=True,
    )


def empty_state(title: str, description: str, icon: str = "○") -> None:
    """Render an intentional zero-data state without inventing any data."""
    st.markdown(
        f"""
        <div class="lg-empty-state">
            <div class="lg-empty-icon">{escape(icon)}</div>
            <div>
                <div class="lg-empty-title">{escape(title)}</div>
                <div class="lg-empty-copy">{escape(description)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, description: str, tone: str = "") -> None:
    """Render a standard KPI card with a non-numeric contextual description."""
    tone_class = f" {escape(tone)}" if tone else ""
    st.markdown(
        f"""
        <div class="lg-metric-card{tone_class}">
            <div class="lg-metric-label">{escape(label)}</div>
            <div class="lg-metric-value">{escape(value)}</div>
            <div class="lg-metric-trend lg-trend-neutral">{escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, tone: str = "gray") -> str:
    """Return consistent semantic badge markup for use inside existing cards."""
    allowed_tones = {"blue", "green", "amber", "red", "purple", "gray"}
    selected_tone = tone if tone in allowed_tones else "gray"
    return f'<span class="lg-badge lg-badge-{selected_tone}">{escape(label)}</span>'
