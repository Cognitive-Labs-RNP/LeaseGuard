"""
Document Management Page for LeaseGuard AI.
Handles uploading and cataloging lease contracts and billing invoices.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Document Management view."""
    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">📁 Document Vault</div>
            <div class="lg-subtitle">Ingest, catalog, and manage lease agreements, amendments, and invoice PDFs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📤 Upload New Documents", "📚 Document Archive"])

    with tab1:
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
            st.success(f"{len(uploaded_files)} file(s) staged. Pipeline execution will trigger in the AI phase.")

    with tab2:
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
