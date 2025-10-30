import os

# --- Configuración de la Base de Datos ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

# --- Configuración de Ollama ---
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

# --- Configuración de JWT para Single Sign-On (SSO) ---
# Se espera que la clave pública se proporcione como una cadena, posiblemente con saltos de línea.
# El archivo .env debe contener la clave en el formato correcto.
JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "RS256")

# --- Otras configuraciones ---
UPLOADS_DIR = "uploads"

# Crear el directorio de subidas si no existe
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
