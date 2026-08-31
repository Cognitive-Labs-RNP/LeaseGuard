"""
Document Vault Page for LeaseGuard AI (Phase 5 Cleanup).
Allows uploading lease contracts, CAM reconciliation statements, and invoices via browser file selection or local system path scanning.
"""

import datetime
import os
import streamlit as st
import pandas as pd
from services.auth import require_auth
from services.supabase import SupabaseService
from services.document_utils import extract_uploaded_text, extract_text_from_filepath
from utils.ui import empty_state, page_header, section_header


def render():
    """Render Document Vault & File Ingestion view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    page_header("Vault", "Document Management", "Upload, inspect, and index commercial lease contracts, amendments, and annual CAM statements.")

    supabase = SupabaseService()
    properties = supabase.get_properties()
    vault_docs = supabase.get_documents()

    if "session_documents" not in st.session_state:
        st.session_state["session_documents"] = []

    # Upload & Ingestion Container
    with st.expander("📥 Ingest Document into Vault", expanded=True):
        if not properties:
            empty_state("No properties added", "Add a property to start monitoring lease compliance and uploading documents.", "○")
            with st.form("quick_add_prop_docs"):
                new_pname = st.text_input("Property Name", placeholder="e.g. Skyline Commercial Center")
                new_pcode = st.text_input("Property Code", placeholder="e.g. PROP-001")
                new_paddr = st.text_input("Address", placeholder="e.g. 100 Financial Plaza, Suite 400")
                new_sqft = st.number_input("Square Footage", value=25000, step=1000)
                if st.form_submit_button("Create Property", type="primary"):
                    if new_pname:
                        supabase.create_property({
                            "name": new_pname,
                            "property_code": new_pcode or "PROP-001",
                            "address": new_paddr or "N/A",
                            "square_footage": float(new_sqft),
                            "status": "Active"
                        })
                        st.success(f"Property '{new_pname}' created!")
                        st.rerun()
                    else:
                        st.error("Property name is required.")
            return

        prop_map = {f"{p.get('code', 'PROP')}: {p.get('name')}": p for p in properties}
        
        ucol1, ucol2, ucol3 = st.columns(3)
        with ucol1:
            selected_prop_label = st.selectbox("Target Property", list(prop_map.keys()))
            selected_prop = prop_map[selected_prop_label]
            selected_prop_id = selected_prop.get("id")
        with ucol2:
            doc_type = st.selectbox("Document Type", ["Lease Agreement", "CAM Reconciliation Statement", "Utility Invoice", "Tax Bill", "Building Amendment", "Lease Photo / Screenshot", "Receipt / Photo Evidence"])
        with ucol3:
            doc_title = st.text_input("Document Title / Reference", placeholder="e.g. 2026_Master_Lease_Amendment.pdf")

        tab_upload, tab_path = st.tabs(["📁 File Uploader / Drag & Drop", "💻 Local System File Path"])

        uploaded_file = None
        local_path = ""

        with tab_upload:
            uploaded_file = st.file_uploader(
                "Browse System Files (PDF, PNG, JPG, Screenshots, Photos, TXT, CSV)",
                type=["pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff", "txt", "csv", "md", "json", "docx"],
                help="Select any PDF, document, photo, or screenshot from your device."
            )

        with tab_path:
            local_path = st.text_input("Local File Path", placeholder="e.g. C:\\Users\\pakhi\\Documents\\lease.pdf", help="Enter full path to a file on your local machine.")

        upload_btn = st.button("📥 Import to Document Vault", type="primary", use_container_width=True)

        if upload_btn:
            if not selected_prop_id:
                st.error("Document import failed: Target property must be selected.")
            elif uploaded_file is None and not local_path.strip() and not doc_title:
                st.warning("Please choose a file, enter a local file path, or provide a document title.")
            else:
                try:
                    fname = "Uploaded_Document.pdf"
                    fsize = "1.2 MB"
                    content_text = ""

                    if uploaded_file is not None:
                        fname = uploaded_file.name
                        fsize = f"{round(uploaded_file.size / 1024, 1)} KB"
                        content_text = extract_uploaded_text(uploaded_file)
                    elif local_path.strip():
                        fname, content_text, size_b = extract_text_from_filepath(local_path.strip())
                        fsize = f"{round(size_b / 1024, 1)} KB"
                    else:
                        fname = doc_title or "Document.pdf"

                    doc_payload = {
                        "property_id": selected_prop_id,
                        "document_type": doc_type,
                        "filename": fname,
                        "file_size": fsize,
                        "storage_path": local_path.strip() or f"documents/{fname}",
                        "content_text": content_text,
                        "status": "Uploaded & Indexed",
                        "Title": fname,
                        "Type": doc_type,
                        "Property": selected_prop.get("name"),
                        "File Size": fsize,
                        "Status": "Uploaded & Indexed",
                        "Date Uploaded": datetime.date.today().strftime("%Y-%m-%d")
                    }

                    # Persist metadata to Supabase
                    saved_doc = supabase.save_document(doc_payload)
                    if saved_doc:
                        st.session_state["session_documents"].insert(0, doc_payload)
                        st.success(f"Document '{fname}' imported successfully and saved to Document Vault!")
                        st.rerun()
                    else:
                        st.error("Document import failed: Database persistence error.")
                except Exception as exc:
                    st.error(f"Unable to import this document: {str(exc)}")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    section_header("Document Vault", "Documents available across the portfolio for review and audit selection.")

    # Combine database vault records and session records
    combined_docs = []
    seen_ids = set()

    for d in vault_docs + st.session_state["session_documents"]:
        did = d.get("id") or d.get("filename") or d.get("Title")
        if did not in seen_ids:
            seen_ids.add(did)
            combined_docs.append({
                "Document ID": d.get("id", f"DOC-{len(seen_ids):02d}"),
                "Filename / Title": d.get("filename") or d.get("Title", "Document.pdf"),
                "Property ID": d.get("property_id") or d.get("Property", "N/A"),
                "Document Type": d.get("document_type") or d.get("Type", "Lease Agreement"),
                "File Size": d.get("file_size") or d.get("File Size", "1.2 MB"),
                "Status": d.get("status") or d.get("Status", "Uploaded & Indexed"),
                "Created At": str(d.get("created_at") or d.get("Date Uploaded") or datetime.date.today())[:10]
            })

    if not combined_docs:
        empty_state("No documents uploaded", "Upload a lease and an invoice or reconciliation statement to run your first audit.", "□")
    else:
        st.dataframe(pd.DataFrame(combined_docs), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
