"""
Document Vault Page for LeaseGuard AI (Phase 5.1 Fixes).
Allows uploading commercial lease contracts and billing statements, associating them with properties, and inspecting parsed files via Supabase.
"""

import datetime
import streamlit as st
import pandas as pd
from services.auth import require_auth
from services.supabase import SupabaseService


def render():
    """Render Document Vault view."""
    user = require_auth()
    if not user:
        st.warning("🔒 Please sign in to access LeaseGuard.")
        return

    st.markdown(
        """
        <div class="lg-header">
            <div class="lg-title">📁 Document Vault</div>
            <div class="lg-subtitle">Upload commercial leases and reconciliation statements associated with portfolio properties.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    supabase = SupabaseService()
    properties = supabase.get_properties()
    vault_docs = supabase.get_documents()

    if "session_documents" not in st.session_state:
        st.session_state["session_documents"] = []

    st.markdown("### 📤 Upload New Document")

    with st.container():
        st.markdown('<div class="lg-card">', unsafe_allow_html=True)

        if not properties:
            st.info("⚠️ No properties available. Please add a commercial property first to upload documents.")
            with st.expander("➕ Add Property Now", expanded=True):
                with st.form("quick_add_prop_docs"):
                    new_pname = st.text_input("Property Name", placeholder="e.g. Skyline Commercial Center")
                    new_pcode = st.text_input("Property Code", placeholder="e.g. PROP-001")
                    new_paddr = st.text_input("Address", placeholder="e.g. 100 Financial Plaza, Suite 400")
                    new_sqft = st.number_input("Square Footage", value=25000, step=1000)
                    if st.form_submit_button("Create Property", type="primary"):
                        if new_pname:
                            supabase.create_property({
                                "name": new_pname,
                                "code": new_pcode or "PROP-001",
                                "address": new_paddr or "N/A",
                                "square_feet": float(new_sqft),
                                "status": "Active"
                            })
                            st.success(f"Property '{new_pname}' created!")
                            st.rerun()
                        else:
                            st.error("Property name is required.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        prop_map = {f"{p.get('code', 'PROP')}: {p.get('name')}": p for p in properties}
        
        ucol1, ucol2, ucol3 = st.columns(3)
        with ucol1:
            selected_prop_label = st.selectbox("Target Property", list(prop_map.keys()))
            selected_prop = prop_map[selected_prop_label]
            selected_prop_id = selected_prop.get("id")
        with ucol2:
            doc_type = st.selectbox("Document Type", ["Lease Agreement", "CAM Reconciliation Statement", "Utility Invoice", "Tax Bill", "Building Amendment"])
        with ucol3:
            doc_title = st.text_input("Document Title / Reference", placeholder="e.g. 2026_Master_Lease_Amendment.pdf")

        uploaded_file = st.file_uploader("Choose PDF or TXT Document File", type=["pdf", "txt"])

        upload_btn = st.button("📥 Upload to Document Vault", type="primary", use_container_width=True)

        if upload_btn:
            if not selected_prop_id:
                st.error("Document upload failed: Target property must be selected.")
            elif uploaded_file is None and not doc_title:
                st.warning("Please choose a file or provide a document title.")
            else:
                try:
                    fname = uploaded_file.name if uploaded_file else (doc_title or "Uploaded_Document.pdf")
                    fsize = f"{round(uploaded_file.size / 1024, 1)} KB" if uploaded_file else "1.2 MB"

                    content_text = ""
                    if uploaded_file is not None:
                        try:
                            content_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                        except Exception:
                            content_text = f"Parsed binary file content for {fname}"

                    doc_payload = {
                        "property_id": selected_prop_id,
                        "document_type": doc_type,
                        "filename": fname,
                        "file_size": fsize,
                        "storage_path": f"documents/{fname}",
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
                        st.success(f"Document '{fname}' uploaded successfully and saved to Document Vault!")
                        st.rerun()
                    else:
                        st.error(f"Document upload failed: Database persistence error.")
                except Exception as exc:
                    st.error(f"Document upload failed: {str(exc)}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Document Storage Vault")

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
        st.info("No documents uploaded yet. Use the form above to upload commercial lease contracts and reconciliation statements.")
    else:
        st.dataframe(pd.DataFrame(combined_docs), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    from utils.css_loader import load_css
    load_css()
    render()
