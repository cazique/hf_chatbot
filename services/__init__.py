"""Service package for ImmoDoc OCR.

This package contains various service modules used by the
application, such as OCR processing, PDF optimisation and
dependency checks.  The implementations provided here are minimal
stubs intended to make the application runnable in the absence of
the real service code.  Real projects should replace these stubs
with proper implementations.
"""

__all__ = [
    "perform_ocr",
    "optimize_pdf",
    "check_dependencies",
    "extract_text_from_pdf",
    "convert_pdf_to_images",
]

from .ocr_service import perform_ocr  # noqa: F401
from .optimize_service import optimize_pdf  # noqa: F401
from .check_deps import check_dependencies  # noqa: F401
from .pdf_actions import extract_text_from_pdf, convert_pdf_to_images  # noqa: F401