# config.py
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "contratos")
DOCS_DIR = os.path.join(BASE_DIR, "documentos")
PLANTILLA_PATH = os.path.join(BASE_DIR, "plantilla_intermediacion.txt")
LEGAL_HTML = os.path.join(BASE_DIR, "legal.html")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Inmobiliaria
INMO = {
    "razon": "HOGAR FAMILIAR INMOBILIARIA, S.L.",
    "cif": "B01755321",
    "domicilio": "Avda de Madrid n° 21, San Fernando de Henares (Madrid)",
    "representante": "Ivan Muñoz León",
    "url": "https://hogarfamiliar.es",
    "email": "contacto@hogarfamiliar.es",
    "dpo": "dpo@hogarfamiliar.es"
}

# Usuarios
USERS = {
    "ivan": "c4ca4238a0b923820dcc509a6f75849b",  # 1234
    "maria": "1a1dc91c907325c69271ddf0c944bc72"  # secreto
}

# Ollama Cloud
OLLAMA_MODEL = "gpt-oss:120b-cloud"  # IA legal potente