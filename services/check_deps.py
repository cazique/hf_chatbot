"""Dependency check utilities.

This module provides functions to check whether external command
line tools required by the OCR and PDF services are available on
the system.  The primary tools checked are Tesseract, Poppler
utilities and Ghostscript.  This stub uses ``shutil.which`` to
determine the presence of commands and returns a mapping of tool
names to boolean availability flags.

In a more comprehensive implementation, version checks and
additional dependencies could be added.
"""

import shutil
from typing import Dict


def check_dependencies() -> Dict[str, bool]:
    """Check the availability of external dependencies.

    This function looks for the ``tesseract``, ``pdftoppm`` (from
    Poppler) and ``gs`` (Ghostscript) executables in the system
    ``PATH`` and returns a dictionary indicating whether each one
    could be located.

    Returns
    -------
    dict
        A mapping of tool names to booleans.  ``True`` means the
        command was found, ``False`` otherwise.
    """
    deps = {
        "tesseract": shutil.which("tesseract") is not None,
        "poppler": shutil.which("pdftoppm") is not None,
        "ghostscript": shutil.which("gs") is not None,
    }
    return deps