"""
Document Management Page for LeaseGuard AI (Phase 3 with RocketRide AI Extraction Test).
"""
import streamlit as st
import pandas as pd
from services.ai import extract_lease_rules

DEFAULT_TEST_LEASE = """ABC Retail Lease has a base annual rent of $120,000.
CAM expenses are capped at $10,000 per year.
The tenant is responsible for 15% of applicable CAM expenses.
Administrative fees may not exceed 5% of CAM expenses.
The landlord must provide an annual CAM reconciliation."""


def render_phase3_ai_test():
    """Render Phase 3 RocketRide Lease Extraction test section."""
    st.markdown("#### 🧪 RocketRide AI Lease Extraction Test (Phase 3)")
    st.caption("Test the RocketRide AI pipeline with Gemini (Primary) and Groq (Fallback) LLMs.")

    test_text = st.text_area(
        "Enter Commercial Lease Document Text:",
        value=DEFAULT_TEST_LEASE,
        height=150,
        help="Paste lease clauses or sample lease text to extract structured rules."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        run_btn = st.button("🚀 Extract Lease Rules (RocketRide Pipeline)", type="primary", use_container_width=True)
    with col2:
        force_fallback = st.checkbox("Simulate Gemini Failure (Test Groq Fallback)", value=False)

    if run_btn:
        if not test_text.strip():
            st.error("Please enter lease text to execute extraction.")
            return

        with st.spinner("Executing RocketRide AI Pipeline..."):
            result = extract_lease_rules(test_text, force_fallback=force_fallback)

        if result["status"] == "success":
            provider = result.get("provider", "unknown")
            if provider == "gemini":
                st.success("✅ Extraction Succeeded via Primary Provider: **Gemini (RocketRide Cloud)**")
            elif provider == "groq":
                st.warning("⚡ Extraction Succeeded via Fallback Provider: **Groq (RocketRide Cloud)**")
                if result.get("primary_error"):
                    st.info(f"ℹ️ Primary Provider Note: {result['primary_error']}")

            data = result.get("data") or {}

            # Display Key Extracted Terms
            st.markdown("##### Extracted Terms Overview")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Base Rent", f"${data.get('base_rent'):,.0f}" if data.get("base_rent") else "N/A", delta=data.get("rent_frequency"))
            m2.metric("CAM Cap", f"${data.get('cam_cap'):,.0f}" if data.get("cam_cap") else "N/A")
            m3.metric("Tenant Share", data.get("tenant_share") or "N/A")
            m4.metric("Admin Fee", data.get("administrative_fee_rules") or "N/A")

            # Structured Data JSON
            with st.expander("📄 View Validated Pydantic JSON Structure", expanded=True):
                st.json(data)

            # Evidence Quotes
            with st.expander("🔍 Extracted Verbatim Evidence Quotes", expanded=False):
                evidence_items = {k: v for k, v in data.items() if k.endswith("_evidence") and v}
                if evidence_items:
                    for k, v in evidence_items.items():
                        st.markdown(f"- **{k}**: *\"{v}\"*")
                else:
                    st.write("No evidence quotes recorded.")
        else:
            st.error(f"❌ AI Pipeline Execution Failed: {result.get('message', 'Unknown error')}")
            if result.get("errors"):
                with st.expander("Technical Error Log"):
                    st.json(result["errors"])


def render():
    """Render Document Management view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">📁 Document Vault & AI Pipelines</div>
            <div class="lg-subtitle">Ingest lease agreements and execute RocketRide AI Extraction pipelines.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_test, tab_upload, tab_archive = st.tabs([
        "🧪 RocketRide AI Extraction Test",
        "📤 Upload New Documents",
        "📚 Document Archive"
    ])

    with tab_test:
        render_phase3_ai_test()

    with tab_upload:
        st.markdown("#### Document Ingestion")
        doc_col1, doc_col2 = st.columns(2)

        with doc_col1:
            doc_type = st.selectbox(
                "Document Classification",
                ["Lease Agreement / Amendment", "CAM Reconciliation Statement", "Utility & Operating Invoice", "Property Tax Assessment"]
            )
            prop_target = st.selectbox(
                "Associated Property",
                ["PROP-001 - Skyline Commercial Center", "PROP-002 - Apex Logistics Hub", "PROP-003 - Harbor Retail Plaza", "PROP-004 - Beacon Medical Center"]
            )

        with doc_col2:
            st.text_input("Document Label / Reference Title", placeholder="e.g. 2026 CAM Year-End True-Up")
            st.date_input("Document Effective Date")

        uploaded_files = st.file_uploader(
            "Upload PDF, TIFF, or DOCX documents",
            type=["pdf", "tiff", "docx", "png", "jpg"],
            accept_multiple_files=True,
            help="Files will be parsed via PyMuPDF and prepared for the RocketRide AI extraction pipeline."
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) staged. Use the RocketRide AI Extraction tab to process documents.")

    with tab_archive:
        st.markdown("#### Ingested Documents")
        sample_docs = pd.DataFrame([
            {
                "Doc ID": "DOC-L-01",
                "Type": "Lease Contract",
                "Property": "Skyline Commercial Center",
                "Filename": "Skyline_Master_Lease_2024.pdf",
                "Status": "Parsed (PyMuPDF Ready)",
                "Uploaded": "2026-08-15"
            },
            {
                "Doc ID": "DOC-I-14",
                "Type": "CAM Statement",
                "Property": "Skyline Commercial Center",
                "Filename": "Skyline_2025_CAM_Reconciliation.pdf",
                "Status": "Pending Audit",
                "Uploaded": "2026-08-20"
            },
            {
                "Doc ID": "DOC-L-02",
                "Type": "Lease Contract",
                "Property": "Harbor Retail Plaza",
                "Filename": "Harbor_Lease_Amendment_1.pdf",
                "Status": "Parsed (PyMuPDF Ready)",
                "Uploaded": "2026-08-22"
            }
        ])
        st.dataframe(sample_docs, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
