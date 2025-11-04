"""Simple OCR service stub.

This module provides a placeholder implementation of the OCR
service used by the ImmoDoc application.  In a real deployment,
this function should call an OCR library such as Tesseract to
extract text from scanned PDF files and output a new searchable
PDF.  For demonstration purposes, this stub simply copies the
input file to a new path and returns success.
"""

import os
import shutil
from typing import Dict


def perform_ocr(file_path: str, lang: str = "spa", deskew: bool = True) -> Dict[str, object]:
    """Perform OCR on a PDF file.

    This stub copies the original file to a new location
    prefixed with ``ocr_`` and returns metadata describing
    success.  In a complete implementation, this function would
    call Tesseract or another OCR engine to create a searchable
    PDF.

    Parameters
    ----------
    file_path: str
        Path to the input PDF.
    lang: str, optional
        Language code for OCR.  This value is accepted for API
        compatibility but ignored in this stub implementation.
    deskew: bool, optional
        Whether to deskew pages before OCR.  This value is accepted
        for API compatibility but ignored in this stub implementation.

    Returns
    -------
    dict
        A dictionary with keys ``success`` (bool), ``output_path``
        (str) and optionally ``error`` (str).
    """
    # Mark parameters as unused to avoid linter warnings
    _ = (lang, deskew)
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        # Create output path by prefixing the filename
        directory, filename = os.path.split(file_path)
        output_filename = f"ocr_{filename}"
        output_path = os.path.join(directory, output_filename)
        shutil.copyfile(file_path, output_path)
        return {"success": True, "output_path": output_path}
    except Exception as exc:
        return {"success": False, "error": str(exc)}