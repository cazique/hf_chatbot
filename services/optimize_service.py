"""PDF optimisation service stub.

This module contains a placeholder implementation for the PDF
optimisation service used by the ImmoDoc application.  In reality,
optimising a PDF would involve recompressing images, removing
unnecessary metadata and reducing the file size.  This stub simply
copies the input file to a new location prefixed with ``opt_``.
"""

import os
import shutil
from typing import Dict


def optimize_pdf(file_path: str) -> Dict[str, object]:
    """Optimise a PDF file.

    This stub copies the original file to a new location
    prefixed with ``opt_`` and returns metadata describing
    success.  In a production system, a PDF library such as
    Ghostscript or qpdf would be invoked to reduce the file size.

    Parameters
    ----------
    file_path: str
        Path to the input PDF.

    Returns
    -------
    dict
        A dictionary with keys ``success`` (bool), ``output_path``
        (str) and optionally ``error`` (str).
    """
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        directory, filename = os.path.split(file_path)
        output_filename = f"opt_{filename}"
        output_path = os.path.join(directory, output_filename)
        shutil.copyfile(file_path, output_path)
        return {"success": True, "output_path": output_path}
    except Exception as exc:
        return {"success": False, "error": str(exc)}