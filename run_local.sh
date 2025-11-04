#!/usr/bin/env bash
# Script para lanzar ImmoDoc OCR en local sin Docker.
# Crea un entorno virtual, instala dependencias y arranca la aplicación.

set -e

# Ensure required directories exist before running the application.  The
# ``uploads`` folder stores uploaded PDFs and ``db`` contains the
# SQLite databases.  When running in Docker these directories are
# mounted via volumes, but for local execution we need to create
# them ourselves.
mkdir -p uploads db

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py