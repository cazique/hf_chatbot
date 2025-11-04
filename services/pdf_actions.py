"""PDF extraction and conversion stubs.

This module supplies rudimentary functions for extracting text
from PDF files and converting PDF pages to images.  In production,
libraries such as PyPDF2, pdfminer.six or pdf2image would be
used.  These stubs merely simulate functionality without
performing real conversions.
"""

import os
from typing import List


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file (stub).

    This stub simply returns a placeholder string indicating that
    real extraction is not implemented.  If the file does not
    exist, an empty string is returned.

    Parameters
    ----------
    file_path: str
        Path to the input PDF.

    Returns
    -------
    str
        The extracted text or a placeholder message.
    """
    if not os.path.exists(file_path):
        return ""
    return "[Texto extraído no disponible en la versión de demostración]"


def convert_pdf_to_images(file_path: str) -> List[str]:
    """Convert a PDF file to a list of image paths (stub).

    This stub pretends to convert each page of the PDF into a PNG
    image.  It simply returns a list with one fake image path per
    page.  If the PDF does not exist, an empty list is returned.

    Parameters
    ----------
    file_path: str
        Path to the input PDF.

    Returns
    -------
    list of str
        A list of strings representing image file paths.
    """
    if not os.path.exists(file_path):
        return []
    # Dummy implementation: pretend the PDF has 1 page and return one image
    directory, filename = os.path.split(file_path)
    basename, _ = os.path.splitext(filename)
    return [os.path.join(directory, f"{basename}_page1.png")]