# ./config.py

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- Configuración de la Aplicación ---
APP_NAME = "Hogar Feliz Chatbot"
APP_VERSION = "1.0.0"
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-dev')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

# --- Configuración de la Base de Datos (MariaDB) ---
DB_USER = os.getenv('MARIADB_USER', 'user')
DB_PASSWORD = os.getenv('MARIADB_PASSWORD', 'password')
DB_NAME = os.getenv('MARIADB_DATABASE', 'chatbot_db')
DB_HOST = os.getenv('MARIADB_HOST', 'db') # Nombre del servicio en docker-compose
DB_PORT = int(os.getenv('MARIADB_PORT', 3306))
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
        # Devuelve un proveedor local por defecto si la variable no está configurada
        return [{
            'name': 'Default Local',
            'url': 'http://localhost:11434',
            'key': 'ollama'
        }]

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

# Exponer la lista de proveedores parseados
PROVIDERS = parse_ollama_providers()

# --- Configuración del Modelo de Lenguaje (LLM) ---
# Opciones: "llama3.1", "llama3", "mistral", "mixtral", "gemma", etc.
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.1))
STREAMING = True # Dejar en True para una mejor experiencia de usuario

# --- Configuración de OCR (Tesseract) ---
# Ruta a Tesseract-OCR si no está en el PATH del sistema.
# En Docker, generalmente está en el PATH si se instala correctamente.
# TESSERACT_CMD = '/usr/bin/tesseract'
