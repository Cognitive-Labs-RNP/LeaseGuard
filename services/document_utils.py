"""Reusable helpers for parsing uploaded lease contracts, CAM statements, invoices, screenshots, and photos."""

from __future__ import annotations

import io
import os
from typing import Tuple


def extract_uploaded_text(file_obj) -> str:
    """Return plain text or metadata extracted from a PDF, TXT, CSV, JSON, or Image upload."""
    if file_obj is None:
        return ""

    try:
        raw = file_obj.getvalue()
    except Exception:
        return ""

    if not raw:
        return ""

    name = (getattr(file_obj, "name", "") or "").lower()

    # Plain text formats
    if name.endswith(".txt") or name.endswith(".md") or name.endswith(".csv") or name.endswith(".json") or name.endswith(".log"):
        try:
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    # PDF documents
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

    # Image files (Screenshots, PNG, JPG, Photos)
    image_exts = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"]
    if any(name.endswith(ext) for ext in image_exts):
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(raw))
            w, h = img.size
            fmt = img.format or "IMAGE"
            return f"[Image Document: {fmt} Screenshot/Photo ({w}x{h} px)]"
        except Exception:
            return "[Image Document: Uploaded Screenshot/Photo]"

    return raw.decode("utf-8", errors="ignore") if raw else ""


def extract_text_from_filepath(file_path: str) -> Tuple[str, str, int]:
    """Read a local file path on the system and return (filename, extracted_text, size_bytes)."""
    file_path = (file_path or "").strip().strip('"').strip("'")
    if not file_path or not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found on system: {file_path}")

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    ext = os.path.splitext(filename)[1].lower()

    if ext in [".txt", ".md", ".csv", ".json", ".log"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return filename, f.read(), file_size

    if ext == ".pdf":
        try:
            import fitz

            doc = fitz.open(file_path)
            parts = []
            for page in doc:
                text = page.get_text("text")
                if text:
                    parts.append(text)
            doc.close()
            return filename, "\n\n".join(parts), file_size
        except Exception as exc:
            raise RuntimeError(f"Unable to read PDF file: {str(exc)}") from exc

    image_exts = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"]
    if ext in image_exts:
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                w, h = img.size
                fmt = img.format or ext.replace(".", "").upper()
                return filename, f"[Image File: {fmt} Photo/Screenshot ({w}x{h} px)]", file_size
        except Exception:
            return filename, f"[Image File: {ext.upper()} Photo/Screenshot]", file_size

    try:
        with open(file_path, "rb") as f:
            raw = f.read()
            return filename, raw.decode("utf-8", errors="ignore"), file_size
    except Exception:
        return filename, "", file_size
