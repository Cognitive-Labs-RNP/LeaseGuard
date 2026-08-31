"""Reusable helpers for parsing uploaded lease and invoice documents."""

from __future__ import annotations

from typing import Optional


def extract_uploaded_text(file_obj) -> str:
    """Return plain text extracted from a PDF or TXT upload.

    Handles invalid and empty PDFs without crashing the app by returning an empty
    string plus a user-friendly error state upstream.
    """
    if file_obj is None:
        return ""

    try:
        raw = file_obj.getvalue()
    except Exception:
        return ""

    if not raw:
        return ""

    name = (getattr(file_obj, "name", "") or "").lower()
    if name.endswith(".txt"):
        try:
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    if name.endswith(".pdf"):
        try:
            import fitz

            doc = fitz.open(stream=raw, filetype="pdf")
            parts = []
            for page in doc:
                text = page.get_text("text")
                if text:
                    parts.append(text)
            doc.close()
            return "\n\n".join(parts)
        except Exception:
            return ""

    return raw.decode("utf-8", errors="ignore") if raw else ""
