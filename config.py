# ./config.py

import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# --- Configuración de la Inmobiliaria ---
INMO = {
    "nombre": "Hogar Feliz Inmobiliaria",
    "representante": "Juan Pérez",
    "cif": "B-01755321",
    "url": "https://hogarfamiliar.es/privacidad"
}

# --- Configuración de Rutas de Plantillas ---
PLANTILLA_PATH = os.path.join(os.path.dirname(__file__), 'plantilla_intermediacion.txt')

# Cargar variables de entorno desde .env
load_dotenv()

# --- Configuración de la Aplicación ---
APP_NAME = "Hogar Feliz Chatbot"
APP_VERSION = "1.0.0"

# --- Configuración de Seguridad ---
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-dev')
JWT_PUBLIC_KEY = os.getenv('JWT_PUBLIC_KEY')
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

# Contexto de encriptación para contraseñas locales
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Usuarios locales como fallback si SSO/JWT no está disponible
LOCAL_USERS = {
    "ivan": "$2b$12$E.E9.Qo8/qGaX3e.d0SOW.IBs1G0T/sT/vtyT7.qmO5g2D23rt/eS", # 1234
    "maria": "$2b$12$6Nl89N1Y1AHe3YqfBqI0z.l1CgP/T8fB32bN8Nq.EK8aAs/5iN.bK"  # secreto
}

# --- Configuración de la Base de Datos (MariaDB) ---
DB_USER = os.getenv('MARIADB_USER', 'user')
DB_PASSWORD = os.getenv('MARIADB_PASSWORD', 'password')
DB_NAME = os.getenv('MARIADB_DATABASE', 'chatbot_db')
DB_HOST = os.getenv('MARIADB_HOST', 'db') # Nombre del servicio en docker-compose
DB_PORT = int(os.getenv('MARIADB_PORT', 3306))

# --- Configuración de Directorios ---
# Crear directorios si no existen
DOCS_DIR = 'uploaded_docs'
PDF_DIR = 'generated_pdfs'
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# --- Configuración de Proveedores OLLAMA ---

def parse_ollama_providers():
    """
    Analiza la variable de entorno OLLAMA_PROVIDERS y la convierte en una lista de diccionarios.
    Formato esperado: "Nombre1|URL1|Clave1,Nombre2|URL2|Clave2"
    """
    providers_str = os.getenv('OLLAMA_PROVIDERS')
    if not providers_str:
        return [{'name': 'Default Local', 'url': 'http://localhost:11434', 'key': 'ollama'}]

    providers_list = []
    providers_data = providers_str.split(',')
    for provider_data in providers_data:
        try:
            name, url, key = provider_data.strip().split('|')
            providers_list.append({'name': name, 'url': url.strip(), 'key': key.strip()})
        except ValueError:
            print(f"Advertencia: El proveedor '{provider_data}' no tiene el formato correcto 'Nombre|URL|Clave' y será ignorado.")
            continue
    return providers_list

PROVIDERS = parse_ollama_providers()

# --- Configuración del Modelo de Lenguaje (LLM) ---
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.1))
STREAMING = True
