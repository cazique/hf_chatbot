# Análisis y Corrección de Proyecto Python

**Exported:** 10/30/2025 18:54:20  
**Link:** [https://gemini.google.com/app/23493afe58455aef](https://gemini.google.com/app/23493afe58455aef)

## Prompt:
> hfloudgemini - Carpeta de código

toma el rol de un experto en python y ollama y por favor analiza este proyecto mio y ayúdame a corregirlo que no me funciona por favor. gracias

igual confírmame la version de python correcta que debería de usar por compatibilidad y tambien si es posible que ejecute esto en un docker en una especie de stack con ollama cloud Maria db etc.. gracias !

## Response:
> Thinking:
> 
> **Examining Project Nuances**
> 
> I've been meticulously analyzing the user's request, focusing on their role as a Python and Ollama expert. The primary task identified is to critically review and assist in correcting their project, implying a focus on debugging and improvement. Currently, I'm working through the technical aspects, determining how best to offer targeted, actionable feedback.
> 
> **Refining the Approach**
> 
> I'm now prioritizing the code analysis of the provided files. My focus is on identifying potential problems based on my Python and Ollama expertise, such as inefficient code or conflicts. I am planning to start by addressing the specific questions regarding the Python version and Docker setup to give concrete feedback first.
> 
> **Deep-diving into Code**
> 
> Now, I'm focusing my attention on `app.py`, looking at the database interaction and the OCR processing as these are often sources of error. Also, I will cross-reference it with `contrato_bot.py` to identify potential redundancies. Finally, I will determine if the usage of the Ollama model is properly configured.
> 
> **Reviewing Potential Conflicts**
> 
> I'm now zeroing in on the file discrepancies. Specifically, the conflicting functionalities in `app.py` and `contrato_bot.py` are a significant concern. I will analyze database interaction and OCR in detail to isolate any errors. I also will verify if the Ollama model is configured for optimal performance. I'm focusing on the overall project structure to ensure efficiency.
> 
> **Identifying Structural Flaws**
> 
> I'm now zeroing in on the file discrepancies. Specifically, the conflicting functionalities in `app.py` and `contrato_bot.py` are a significant concern. I will analyze database interaction and OCR in detail to isolate any errors. I also will verify if the Ollama model is configured for optimal performance. I'm focusing on the overall project structure to ensure efficiency.
> 
> I am starting to formulate recommendations on how to clean up the code, especially by streamlining the functions. The key areas of interest are the database interactions and OCR processes, along with potential issues with the Docker configuration. Finally, I need to check the import statements.
> 
> **Analyzing Code Structure**
> 
> I'm now investigating the inconsistencies in the project, particularly between `app.py` and `contrato_bot.py`. I've started examining the `db.py` file for database interactions and I'm looking at potential conflicts with the `config.py` file. I plan to check all import statements.
> 
> **Reviewing Code Structure**
> 
> I'm now investigating the inconsistencies in the project, particularly between `app.py` and `contrato_bot.py`. I've started examining the `db.py` file for database interactions and I'm looking at potential conflicts with the `config.py` file. I plan to check all import statements. I'm also considering the use of SQLite3 over MariaDB, given the database file being SQLite3.
> 
> **Reviewing Project Discrepancies**
> 
> I've been analyzing the inconsistencies within the project's code structure, mainly between `app.py` and `contrato_bot.py`. I've begun to examine the database interactions within `db.py` to identify potential issues, and I will check any conflicts with the `config.py` file, as well as the imports. I'm also considering the use of SQLite3 given the database format.
> 
> **Reviewing Code Structure**
> 
> I'm now investigating the inconsistencies in the project, particularly between `app.py` and `contrato_bot.py`. I've started examining the `db.py` file for database interactions and I'm looking at potential conflicts with the `config.py` file. I plan to check all import statements. I'm also considering the use of SQLite3 over MariaDB, given the database file being SQLite3.
> 
> **Examining Code Discrepancies**
> 
> I've been analyzing the inconsistencies within the project's code structure, mainly between `app.py` and `contrato_bot.py`. I've begun to examine the database interactions within `db.py` to identify potential issues, and I will check any conflicts with the `config.py` file, as well as the imports. I'm also considering the use of SQLite3 given the database format. I'm starting to review the database usage given that I'm considering using SQLite3.
> 
> **Analyzing Project Structure**
> 
> I've been examining the inconsistencies in the project, particularly between `app.py` and `contrato_bot.py`. I've started examining the `db.py` file for database interactions and I'm looking at potential conflicts with the `config.py` file. I plan to check all import statements. I'm also considering the use of SQLite3 over MariaDB, given the database file being SQLite3.
> 
> I'm currently reviewing the project's code to determine the most effective approach for making corrections. My focus is on ensuring the accuracy and efficiency of the code base.
> 
> **Reviewing Code Structure**
> 
> I'm currently reviewing the project's code to determine the most effective approach for making corrections. My focus is on ensuring the accuracy and efficiency of the code base.

¡Hola! Como experto en Python y Ollama, he analizado la estructura de tu proyecto. Tienes una base muy sólida aquí, pero veo varios conflictos y un error crítico que probablemente sea la causa de que no funcione.

Aquí tienes mi análisis y las correcciones:

Análisis del Proyecto y Correcciones Urgentes
---------------------------------------------

He identificado varios problemas, pero el más importante es un conflicto entre dos archivos de aplicación y un error de importación en tu lógica de base de datos.

### 1\. Conflicto Principal: `app.py` vs. `contrato_bot.py`

Tienes dos archivos que intentan hacer lo mismo: `hfloudgemini/app.py` y `hfloudgemini/contrato_bot.py`.

*   **`app.py`** es modular: Importa correctamente `db.py`, `ocr_utils.py`, `pdf_utils.py` y `config.py`. Parece ser la versión más actualizada y correcta.
*   **`contrato_bot.py`** es monolítico: Redefine su propia lógica de OCR, generación de PDF y variables de usuario, ignorando tus otros archivos de utilidades.

Esta duplicación crea conflictos. Por ejemplo, `app.py` usa `hashlib.md5` para las contraseñas, que coincide con los hashes en `config.py`. Sin embargo, `contrato_bot.py` usa `hashlib.sha256`, por lo que el login fallaría si intentas ejecutar ese archivo.

**➡️ Corrección:** Te recomiendo **eliminar o archivar `hfloudgemini/contrato_bot.py`** y centrar todos tus esfuerzos en `hfloudgemini/app.py`.

### 2\. Error Crítico en `db.py` (Probable Causa del Fallo)

Tu archivo `hfloudgemini/db.py` intenta guardar la fecha actual en las funciones `guardar_contrato` y `guardar_documento` usando `datetime.now()`.

Sin embargo, **nunca importas la librería `datetime`** en ese archivo. Esto provocará un error `NameError: name 'datetime' is not defined` cada vez que intentes guardar algo en la base de datos.

**➡️ Corrección:** Añade la siguiente línea al principio de tu archivo `hfloudgemini/db.py`:

```
# db.py - SQLite
import sqlite3
import os
from datetime import datetime  # <--- AÑADIR ESTA LÍNEA
from config import BASE_DIR
...
```

### 3\. Inconsistencia Menor en `app.py`

En `hfloudgemini/app.py`, llamas al modelo de Ollama usando un string hardcodeado: `respuesta = ollama.chat(model='gpt-oss:120b-cloud', ...)`

Sin embargo, ya tienes este valor definido en tu archivo `config.py` (`OLLAMA_MODEL = "gpt-oss:120b-cloud"`).

**➡️ Corrección (Recomendada):** Importa y usa la variable de configuración para mantener tu código limpio:

```
# app.py
...
# Importa la variable OLLAMA_MODEL junto con las demás
from config import USERS, OUTPUT_DIR, DOCS_DIR, INMO, OLLAMA_MODEL
...

# En la función main, usa la variable
respuesta = ollama.chat(
    model=OLLAMA_MODEL,  # <--- USA LA VARIABLE
    messages=[{'role': 'user', 'content': msg.content}]
)
...
```

* * *

Versión de Python Recomendada
-----------------------------

Para un proyecto que usa `chainlit`, `ollama`, `opencv-python` (cv2), `pytesseract` y sintaxis moderna como f-strings y type hints (ej. `msg: cl.Message`), una versión estable de Python es crucial.

*   **Recomendación:** **Python 3.10** o **Python 3.11**.
*   **Mínimo:** Python 3.8+.

Cualquiera de estas versiones te asegurará compatibilidad con todas las dependencias del proyecto.

* * *

Docker y el "Stack" (Ollama Cloud y MariaDB)
--------------------------------------------

¡Absolutamente! Puedes y debes ejecutar esto en un Docker. Sin embargo, hay un par de aclaraciones importantes basadas en tu código:

### 1\. Ollama Cloud

**No "dockerizas" Ollama Cloud**. Como el nombre indica, es un servicio en la nube (Cloud). Tu aplicación en Python (`app.py`) simplemente realiza una llamada API a ese servicio a través de Internet.

*   **Tu Stack de Docker:** Tu contenedor de Docker solo necesita la aplicación Python (Chainlit) y acceso a Internet para poder contactar con la API de `gpt-oss:120b-cloud`. No necesitas un servicio de "Ollama" en tu `docker-compose.yml`.

### 2\. SQLite vs. MariaDB

**Tu proyecto NO usa MariaDB**. Estás usando **SQLite**, que es una base de datos basada en un solo archivo (`hogar_familiar.db`).

Esto simplifica enormemente tu stack de Docker:

*   **Stack Simple (Recomendado):**
    1.  **Servicio `app`:** Un contenedor con Python 3.10 que instala tus `requirements.txt` y ejecuta `chainlit run app.py -w`.
    2.  **Volumen:** Simplemente necesitas montar tu base de datos SQLite como un volumen para que los datos persistan.
        *   `volumes: ./hogar_familiar.db:/app/hogar_familiar.db`
*   **Si _realmente quieres_ migrar a MariaDB:**
    1.  Añadirías un servicio `mariadb` a tu `docker-compose.yml`.
    2.  Instalarías un driver de Python (ej. `mysql-connector-python` o `pymysql`).
    3.  **Tendrías que reescribir completamente tu archivo `db.py`** para usar las conexiones, cursores y sintaxis SQL de MariaDB en lugar de `sqlite3`.

### Resumen de Próximos Pasos

1.  **Aplica la corrección crítica:** Añade `from datetime import datetime` a `hfloudgemini/db.py`.
2.  **Elimina el conflicto:** Borra o renombra `hfloudgemini/contrato_bot.py` para evitar confusiones.
3.  **Ejecuta `app.py`:** Intenta iniciar tu aplicación de nuevo.

Si después de estos cambios sigues teniendo problemas, por favor, **copia y pega el error exacto** que ves en tu consola. Sin el error específico, solo puedo depurar los problemas obvios del código. ¡Espero que esto lo solucione!

## Prompt:
Vale entonces, es factible desarrollar dentro de un docker ? uso jetbrains pycharm, vamos creando un stack ? me ayudas ?

mariadb

subdoiminio de momento chat.jorgemc.casa

ollama y no se que mas

y me enviarías el codigo completo corregido de cada archivo que hay que modificar gracias

analiza bien el codigo completo de todo

## Response:
> Thinking:
> 
> **Analyzing User Feedback**
> 
> I've been meticulously analyzing the user's feedback, focusing on their acceptance of the previous breakdown. I'm now honing in on the core question regarding faith, actively deciphering its nuances. This process is crucial for crafting a relevant and insightful response.
> 
> **Refining Docker Strategy**
> 
> I'm now zeroing in on the best approach for the user's Docker transition, considering their specific needs. It seems they want a full stack, incorporating MariaDB and subdomains, and I need to clarify the Ollama Cloud API integration. I'm focusing on the code migration and ensuring a smooth workflow.
> 
> **Developing the MariaDB Solution**
> 
> I'm now deep into crafting the MariaDB solution, recognizing the user's explicit request. This requires a full rewrite of `db.py` to seamlessly integrate with a Dockerized MariaDB instance. I've also updated the `docker-compose.yml` to include the database service and incorporated the necessary Python driver in `requirements.txt`. I am also working on the subdomain details.
> 
> **Implementing MariaDB Integration**
> 
> I'm now fully immersed in developing the MariaDB integration. This involves a full rewrite of `db.py` to seamlessly connect with a Dockerized MariaDB instance, reading database credentials securely from environment variables. I've updated the `docker-compose.yml` file to include the MariaDB service and adjusted the `requirements.txt` to include the `mysql-connector-python` driver. I'm also preparing to address the subdomain aspect as a separate deployment consideration, noting that this stack will initially run on `localhost`.
> 
> **Finalizing the MariaDB Setup**
> 
> I'm now fully immersed in developing the MariaDB integration. This involves a complete rewrite of `db.py` to seamlessly interface with a Dockerized MariaDB instance. I've updated the `docker-compose.yml` file to include the MariaDB service and adjusted the `requirements.txt` to include the `mysql-connector-python` driver. I'm also preparing to address the subdomain aspect as a separate deployment consideration, noting that this stack will initially run on `localhost`. I've added error handling in the database interactions.
> 
> **Constructing Docker Compose**
> 
> I'm currently crafting the `docker-compose.yml` file, focusing on integrating MariaDB as the primary database service, while also ensuring the application container can access the Ollama Cloud API. I'm taking care to clarify the distinction between the development and deployment aspects, especially regarding the subdomain. I'll provide this file for a localhost initial setup.
> 
> **Designing the Development Stack**
> 
> I'm presently creating the Docker setup, which centers on seamlessly integrating MariaDB, as requested. The Docker Compose file will define both the MariaDB service and the application container. The subdomain will be clarified as part of a separate deployment process. Error handling in the database interaction is addressed.
> 
> **Designing the Docker Stack**
> 
> I'm now fully immersed in the process of designing the Docker stack, including MariaDB integration. My current focus is on building the Docker Compose file to provide a localhost setup. This will address the user's requirement. I've also identified potential changes to the `config.py` file, incorporating error handling.
> 
> **Developing Docker Setup**
> 
> I've completed the preliminary designs for the Docker stack, with the core focus on MariaDB integration, as requested. The localhost setup will be provided in a Docker Compose file. I'm also preparing code edits for the `config.py` file to incorporate error handling and environment variables.
> 
> **Developing Docker Compose**
> 
> I've crafted the core `docker-compose.yml` file, focusing on integrating MariaDB as the primary database service. Now I'm working on the error handling in database interactions to complete the setup. The localhost details have been incorporated for the initial setup.
> 
> **Designing Docker Configuration**
> 
> I'm now focused on constructing the Docker configuration, with the user's MariaDB request at the forefront. I'm building a Docker Compose file tailored for their need. My work will provide a comprehensive solution for their localhost setup.
> 
> **Crafting Docker Configuration**
> 
> I'm presently building the Docker Compose file, recognizing the user's MariaDB requirement as the highest priority. I've designed the `docker-compose.yml` and `Dockerfile`, focusing on providing a well-structured localhost setup. I'm working to make the setup simple for them.

¡Claro que sí! Es totalmente factible y, de hecho, es la forma profesional de trabajar. Usar PyCharm con un intérprete de Docker (basado en `docker-compose`) es la combinación perfecta.

Vamos a crear ese stack. Has pedido MariaDB, así que **migraremos tu proyecto de SQLite a MariaDB**. Esto requiere cambiar tu archivo `db.py` por completo.

Aquí tienes un análisis completo y todos los archivos que necesitas.

* * *

Tu Stack de Desarrollo (Docker y MariaDB)
-----------------------------------------

Este será nuestro stack:

1.  **Servicio `app` (Tu código):** Un contenedor Docker con Python 3.10.
    *   Instalará todas las dependencias (Chainlit, Ollama, OpenCV, Tesseract OCR).
    *   Ejecutará tu `app.py`.
    *   PyCharm se conectará a este contenedor como su intérprete.
2.  **Servicio `mariadb` (Base de Datos):** Un contenedor estándar de MariaDB.
    *   El servicio `app` se conectará a él para guardar los datos.
    *   Los datos se guardarán en un "volumen" de Docker para que no se borren.

### Aclaraciones Importantes:

*   **Ollama vs. Ollama Cloud:** Tu `config.py` y `app.py` usan el modelo `gpt-oss:120b-cloud`. Esto **no** es un servicio que instalas en Docker, sino una **API en la nube** a la que llamas. Por lo tanto, **no añadiremos un servicio "Ollama"** al stack. Tu contenedor `app` solo necesita acceso a internet para llamarlo.
*   **Subdominio (`chat.jorgemc.casa`):** Eso es para **despliegue (producción)**, no para desarrollo. Se configura fuera de este stack, usando un "reverse proxy" (como Nginx o Traefik) y apuntando tu DNS a la IP de tu servidor. Durante el desarrollo, accederás a tu app simplemente vía `http://localhost:8000`.

* * *

1\. Archivos para el Stack (Nuevos)
-----------------------------------

Crea estos 3 archivos en la raíz de tu proyecto (la carpeta `hfloudgemini/`):

### `docker-compose.yml`

(Este archivo define tu stack completo)

```
version: '3.8'

services:
  app:
    build: .
    command: chainlit run app.py -w --port 8000 --host 0.0.0.0
    ports:
      - "8000:8000"
    volumes:
      # Monta tu código para que los cambios se reflejen al instante
      - .:/app
    environment:
      # Credenciales para conectar a MariaDB
      - DB_HOST=mariadb
      - DB_USER=hogar_user
      - DB_PASS=hogar_pass
      - DB_NAME=hogar_familiar_db
    depends_on:
      - mariadb

  mariadb:
    image: mariadb:10.6
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: root_password_segura
      MYSQL_DATABASE: hogar_familiar_db
      MYSQL_USER: hogar_user
      MYSQL_PASSWORD: hogar_pass
    volumes:
      - mariadb_data:/var/lib/mysql
    ports:
      # Opcional: Expone el puerto de MariaDB a tu PC
      - "3307:3306" 

volumes:
  mariadb_data:
```

### `Dockerfile`

(Este archivo define cómo construir tu contenedor `app`)

```
# Usamos una imagen oficial de Python 3.10
FROM python:3.10-slim

# Instalamos Tesseract OCR y el paquete de idioma español
# Esto es CRÍTICO para que ocr_utils.py funcione
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo de requisitos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de tu proyecto
COPY . .

# Exponemos el puerto 8000 (el que usa Chainlit)
EXPOSE 8000
```

### `requirements.txt`

(Lista de todas las dependencias de Python)

```
chainlit
ollama
Pillow
pytesseract
opencv-python-headless
numpy
reportlab
jinja2
mysql-connector-python
```

* * *

2\. Código Corregido (Archivos Modificados)
-------------------------------------------

Aquí está el código completo y corregido para los archivos que lo necesitaban.

### `hfloudgemini/db.py` (Reescrito para MariaDB)

(Este es el cambio más grande. Borra el contenido de tu `db.py` y reemplázalo con esto)

```
# db.py - MariaDB/MySQL
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_CONFIG
import json

def get_db_connection():
    """Crea y devuelve una conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                usuario TEXT,
                fecha DATETIME,
                pdf_path TEXT,
                datos_json LONGTEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                contrato_id INTEGER,
                tipo TEXT,
                nombre_archivo TEXT,
                ruta TEXT,
                ocr_text LONGTEXT,
                fecha_subida DATETIME,
                FOREIGN KEY (contrato_id) REFERENCES contratos(id)
            )
        ''')
        conn.commit()
    except Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn.is_connected():
            c.close()
            conn.close()

def guardar_contrato(usuario, pdf_path, datos):
    """Guarda un nuevo contrato en la base de datos."""
    conn = get_db_connection()
    if conn is None:
        return None
    
    contrato_id = None
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO contratos (usuario, fecha, pdf_path, datos_json) VALUES (%s, %s, %s, %s)",
            (usuario, datetime.now(), pdf_path, datos) # 'datos' ya es json.dumps en app.py
        )
        conn.commit()
        contrato_id = c.lastrowid
    except Error as e:
        print(f"Error al guardar contrato: {e}")
    finally:
        if conn.is_connected():
            c.close()
            conn.close()
    return contrato_id

def guardar_documento(contrato_id, tipo, nombre, ruta, ocr_text):
    """Guarda un documento asociado a un contrato."""
    conn = get_db_connection()
    if conn is None:
        return
        
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO documentos (contrato_id, tipo, nombre_archivo, ruta, ocr_text, fecha_subida) VALUES (%s, %s, %s, %s, %s, %s)",
            (contrato_id, tipo, nombre, ruta, ocr_text, datetime.now())
        )
        conn.commit()
    except Error as e:
        print(f"Error al guardar documento: {e}")
    finally:
        if conn.is_connected():
            c.close()
            conn.close()
```

### `hfloudgemini/config.py` (Modificado para Docker)

(Reemplaza tu `config.py` con esto)

```
# config.py
import os
from datetime import datetime

# Paths (relativos al WORKDIR /app en Docker)
OUTPUT_DIR = "contratos"
DOCS_DIR = "documentos"
PLANTILLA_PATH = "plantilla_intermediacion.txt"
LEGAL_HTML = "legal.html"

# Crear directorios si no existen
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Configuración de MariaDB (leída desde variables de entorno de Docker)
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS', ''),
    'database': os.environ.get('DB_NAME', 'test_db')
}

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

# Usuarios (Contraseñas son "1" y "secreto")
USERS = {
    "ivan": "c4ca4238a0b923820dcc509a6f75849b",  # md5("1")
    "maria": "1a1dc91c907325c69271ddf0c944bc72" # md5("secreto")
}

# Ollama Cloud
OLLAMA_MODEL = "gpt-oss:120b-cloud"
```

### `hfloudgemini/app.py` (Corregido para usar Config)

(Reemplaza tu `app.py`. El único cambio es usar la variable `OLLAMA_MODEL` de tu config)

```
# app.py - VERSIÓN CORREGIDA Y FUNCIONAL 100%
import chainlit as cl
import ollama
import hashlib
import os
from datetime import datetime
# Usamos OLLAMA_MODEL de la config
from config import USERS, OUTPUT_DIR, DOCS_DIR, INMO, OLLAMA_MODEL 
from ocr_utils import procesar_dni
from pdf_utils import generar_pdf
from db import init_db, guardar_contrato, guardar_documento
import json

# === INICIALIZACIÓN ===
init_db()

@cl.on_chat_start
async def start():
    # CONFIGURACIÓN DE PÁGINA AL INICIO
    cl.set_page_config(
        title="Hogar Familiar | Asistente Legal IA",
        description="Contratos, OCR, IA legal actualizada",
        favicon="public/favicon.ico"
    )

    # Login
    if not cl.user_session.get("logged_in"):
        await login_flow()
        return

    # Saludo personalizado
    user = cl.user_session.get("username", "Usuario").capitalize()
    hora = datetime.now().hour
    saludo = "¡Buenos días" if 5 <= hora < 12 else "¡Buenas tardes" if hora < 20 else "¡Buenas noches"
    await cl.Message(content=f"{saludo}, **{user}**! ¿En qué te ayudo hoy?").send()

    # Footer legal
    await cl.run_js("""
    setTimeout(() => {
      const footer = document.createElement('div');
      footer.style.cssText = 'text-align:center; font-size:11px; color:#888; margin:20px 0; line-height:1.4;';
      footer.innerHTML = `
        <strong>Sistema Privado</strong> • Solo para personal y clientes de
        <strong>Hogar Familiar Inmobiliaria</strong> (CIF B-01755321).<br>
        <a href="/legal.html" style="color:#1a73e8;">Ver términos legales</a>
      `;
      document.body.appendChild(footer);
    }, 500);
    """)

async def login_flow():
    await cl.Message(content="Inicia sesión para continuar").send()
    user_resp = await cl.AskUserMessage(content="Usuario:", timeout=60).send()
    username = user_resp["content"].strip().lower()
    if username not in USERS:
        await cl.Message(content="Usuario incorrecto").send()
        await login_flow()
        return
    pass_resp = await cl.AskUserMessage(content="Contraseña:", password=True, timeout=60).send()
    password = pass_resp["content"]
    if hashlib.md5(password.encode()).hexdigest() != USERS[username]:
        await cl.Message(content="Contraseña incorrecta").send()
        await login_flow()
        return
    cl.user_session.set("logged_in", True)
    cl.user_session.set("username", username)
    await cl.Message(content="Login correcto").send()

@cl.on_message
async def main(msg: cl.Message):
    if not cl.user_session.get("logged_in"):
        await start()
        return

    s = cl.user_session
    username = s.get("username", "usuario")

    # === SUBIDA DE DOCUMENTOS ===
    if msg.elements:
        await cl.Message(content="Procesando documento(s)...").send()
        docs = s.get("documentos", [])
        for el in msg.elements:
            if el.type == "image":
                es_anverso = len([d for d in docs if "anverso" in d.get("ruta", "")]) == 0
                data = procesar_dni(el.path, es_anverso)
                docs.append(data)
                await cl.Message(content=f"Detectado: **{data['nombre']}** (DNI: {data['dni']})").send()
                # Guardar en DB
                # Usamos un ID de contrato temporal '1' si no existe uno real
                contrato_id = s.get("contrato_id", 1) 
                guardar_documento(contrato_id, "DNI", os.path.basename(data["ruta"]), data["ruta"], data["ocr"])
        s.set("documentos", docs)

    # === COMANDOS DE TEXTO ===
    else:
        text = msg.content.lower().strip()

        if "generar contrato" in text:
            await generar_contrato_flow(s, username)

        elif text in ["ya está", "finalizar", "generar pdf"]:
            if s.get("documentos"):
                await generar_pdf_documentos(s, username)
            else:
                await cl.Message(content="No hay documentos subidos.").send()

        elif "legal" in text or "ley" in text or "normativa" in text:
            respuesta = ollama.chat(
                model=OLLAMA_MODEL, # <- USANDO VARIABLE DE CONFIG
                messages=[{'role': 'user', 'content': msg.content}]
            )
            await cl.Message(content=respuesta['message']['content']).send()

        else:
            # IA general
            try:
                respuesta = ollama.chat(
                    model=OLLAMA_MODEL, # <- USANDO VARIABLE DE CONFIG
                    messages=[{'role': 'user', 'content': msg.content}]
                )
                await cl.Message(content=respuesta['message']['content']).send()
            except Exception as e:
                await cl.Message(content="Error con IA. Prueba de nuevo.").send()

async def generar_contrato_flow(s, username):
    docs = s.get("documentos", [])
    if not docs:
        await cl.Message(content="Primero sube los DNIs.").send()
        return

    # Preguntas
    lugar = (await cl.AskUserMessage(content="Lugar de firma (ej: Los Santos de la Humosa):")).get("content")
    direccion = (await cl.AskUserMessage(content="Dirección del inmueble:")).get("content")
    precio = (await cl.AskUserMessage(content="Precio de venta (€):")).get("content")
    honorarios = (await cl.AskUserMessage(content="Honorarios (€ IVA excl.):")).get("content")
    exclusividad = (await cl.AskUserMessage(content="Exclusividad (sí/no):")).get("content")
    meses = (await cl.AskUserMessage(content="Duración (meses):")).get("content")
    jurisdiccion = (await cl.AskUserMessage(content="Jurisdicción:")).get("content")

    # Construir datos
    lista = [f"D. {d['nombre']}, DNI {d['dni']}, domicilio en {direccion}" for d in docs]
    datos = {
        "LUGAR": lugar,
        "LISTA_VENDEDORES": " y ".join(lista),
        "ES_SON": "es" if len(docs) == 1 else "son",
        "DIRECCION_INMBULE": direccion, # Corregido: 'DIRECCION_INMUEBLE'
        "DIRECCION_INMUEBLE": direccion,
        "PRECIO_VENTA": precio,
        "HONORARIOS": honorarios,
        "EXCLUSIVIDAD": exclusividad.title(),
        "DURACION_MES": meses,
        "JURISDICCION": jurisdiccion,
        "FIRMAS_VENDEDORES": "\n".join([f"[Firma {i+1}]" for i in range(len(docs))])
    }

    # Generar PDF
    pdf_name = f"intermediacion_{username}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
    generar_pdf(datos, pdf_path, username)

    # Guardar en DB
    contrato_id = guardar_contrato(username, pdf_path, json.dumps(datos))
    s.set("contrato_id", contrato_id)

    # Actualizar documentos con el ID de contrato correcto
    for doc in docs:
        guardar_documento(contrato_id, "DNI", os.path.basename(doc["ruta"]), doc["ruta"], doc["ocr"])

    await cl.Message(
        content="Contrato generado",
        elements=[cl.File(path=pdf_path, name=pdf_name)]
    ).send()
    s.set("documentos", []) # Limpiar documentos después de generar

async def generar_pdf_documentos(s, username):
    docs = s.get("documentos", [])
    if not docs:
        await cl.Message(content="No hay documentos.").send()
        return

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    pdf_path = os.path.join(OUTPUT_DIR, f"documentos_{username}_{datetime.now():%Y%m%d_%H%M%S}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 50

    for doc in docs:
        c.drawString(50, y, f"DNI: {doc['dni']} - {doc['nombre']}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()

    await cl.Message(content="PDF de documentos generado", elements=[cl.File(path=pdf_path)]).send()
```

* * *

3\. Archivo a Eliminar
----------------------

*   **`hfloudgemini/contrato_bot.py`**: **DEBES ELIMINAR ESTE ARCHIVO.** Es una versión antigua y monolítica que entra en conflicto directo con `app.py`.

Cómo Usar esto en PyCharm
-------------------------

1.  Asegúrate de tener **PyCharm Professional** (la versión Community no tiene integración con Docker).
2.  Asegúrate de tener **Docker Desktop** instalado y ejecutándose.
3.  Crea los 3 archivos nuevos (`docker-compose.yml`, `Dockerfile`, `requirements.txt`) en tu carpeta `hfloudgemini`.
4.  Reemplaza el código de `db.py`, `config.py`, y `app.py` con las versiones que te he dado.
5.  Elimina `contrato_bot.py`.
6.  En PyCharm, ve a `Settings` \> `Project: hfloudgemini` \> `Python Interpreter`.
7.  Haz clic en el icono de engranaje \> `Add...`
8.  Selecciona `Docker Compose`.
9.  Asegúrate de que el `Configuration file(s)` apunte a tu `docker-compose.yml`.
10.  En `Service`, selecciona `app`.
11.  PyCharm configurará todo. Haz clic en el botón verde de "Run" (▶️) en la parte superior. PyCharm ejecutará `docker-compose up` y tu app estará disponible en `http://localhost:8000`.

## Prompt:
\# config.py

import os

from datetime import datetime

\# Paths (relativos al WORKDIR /app en Docker)

OUTPUT\_DIR = "contratos"

DOCS\_DIR = "documentos"

PLANTILLA\_PATH = "plantilla\_intermediacion.txt"

LEGAL\_HTML = "legal.html"

\# Crear directorios si no existen

os.makedirs(OUTPUT\_DIR, exist\_ok=True)

os.makedirs(DOCS\_DIR, exist\_ok=True)

\# Configuración de MariaDB (leída desde variables de entorno de Docker)

DB\_CONFIG = {

    'host': os.environ.get('DB\_HOST', 'localhost'),

    'user': os.environ.get('DB\_USER', 'root'),

    'password': os.environ.get('DB\_PASS', ''),

    'database': os.environ.get('DB\_NAME', 'test\_db')

}

\# Inmobiliaria

INMO = {

    "razon": "HOGAR FAMILIAR INMOBILIARIA, S.L.",

    "cif": "B01755321",

    "domicilio": "Avda de Madrid n° 21, San Fernando de Henares (Madrid)",

    "representante": "Ivan Muñoz León",

    "url": "https://hogarfamiliar.es",

    "email": "contacto@hogarfamiliar.es",

    "dpo": "dpo@hogarfamiliar.es"

}

\# Usuarios (Contraseñas son "1" y "secreto")

USERS = {

    "ivan": "c4ca4238a0b923820dcc509a6f75849b",  # md5("1")

    "maria": "1a1dc91c907325c69271ddf0c944bc72" # md5("secreto")

}

\# Ollama Cloud

OLLAMA\_MODEL = "gpt-oss:120b-cloud"

el config.py me gustaría si se puede añadir o si tiene opcion este framework de chatbot para poder configurar e inclljuso añadir posibles variables no se si es posible, tambien añade el subdominio chat.jorgemc.casa como te comente para que mis compañeros que viven fuera puedan verlo, igualmente este haz una búsqueda actual y dime que plugin addons o frameworks o lo que sea suele utilizar la gente para seguridad, utilizados lo que fuese

tambien asegurarons de que existe un historial de chat, proyectos, etc...

## Response:
> Thinking:
> 
> **Reflecting on Config.py**
> 
> I'm currently thinking about how to adapt the `config.py` file. Specifically, I'm considering whether I can introduce additional variables. The aim is to make configuration more streamlined.
> 
> **Clarifying Configuration Scope**
> 
> I'm now thinking about how to best communicate the scope of `config.py`. While adding variables is straightforward, I need to emphasize that the subdomain setup is _not_ a code change. It's a deployment configuration, involving DNS, a VPS, and a reverse proxy. I'm also planning a security deep dive, and will be using Google search tools to help.
> 
> **Exploring Chat History Persistence**
> 
> I'm now thinking about how to best save chat history. I'm considering adding a dedicated table to the database. This would allow for persistent, multi-user conversations, which is crucial for the projects' ongoing nature. I'll need to explore how Chainlit's capabilities can complement this.
> 
> **Considering Persistence Strategy**
> 
> My focus has shifted towards the chat history database implementation. To ensure project continuity and enable multi-user conversations, I am exploring adding a dedicated table within the database, which would complement Chainlit's existing persistence methods. This will provide a robust method of storing chat histories.
> 
> **Reviewing Config Options**
> 
> I'm currently investigating how Chainlit's configuration possibilities can be extended. I'm focusing on ways to introduce more customizable variables within a `.py` configuration file. My goal is to determine the feasibility of adding and managing these variables seamlessly.
> 
> **Defining Variable Scope**
> 
> I'm now clarifying the interplay between `config.py`, environment variables, and Chainlit's built-in configuration. Specifically, I'm integrating best practices for local development using a `.env` file, contrasting it with the existing `os.environ` setup ideal for containerized deployments. I'll emphasize the benefits of each approach to best support flexible variable management.
> 
> **Enhancing Deployment**
> 
> I'm now focusing on the production deployment setup. I'm clarifying the steps needed to host the application on a custom subdomain, such as `chat.jorgemc.casa`. This involves setting up DNS, a cloud server (VPS), and a reverse proxy (like Traefik, which I'll recommend due to its Docker Compose integration). I'll provide clear instructions on how to configure the `docker-compose.yml` file to handle the subdomain and secure HTTPS connections using Let's Encrypt.
> 
> **Implementing Security Measures**
> 
> I'm now integrating robust security measures. I've delved into Fast API's offerings, which are relevant to Chainlit's underlying framework. I'll advise integrating middleware for headers and CORS, and I plan to highlight the benefits of using a strong password hashing library like `passlib` to supersede the current weak hashing method. Additionally, I'll recommend tools like `bandit` and `pip-audit` for code vulnerability scanning and dependency audits as part of the CI/CD pipeline.
> 
> **Refining Database Interaction**
> 
> I'm now revising my plans to make sure the chat history is saved correctly. I'll modify `db.py` to add the `chat_history` table and `app.py` to use it, loading previous chats at start and saving each user/bot turn. This ensures continuity and incorporates all crucial project and document data from the previous database implementation.
> 
> **Finalizing Chat History Implementation**
> 
> I've now incorporated the chat history persistence. I've updated both the database and the application files to correctly store and retrieve user conversations. When the application starts, it loads the previous chat history from the database and displays it to the user. I also ensured that new messages are saved in the correct format. This integration provides a continuous conversation experience and preserves all critical data.
> 
> **Refining Security Integration**
> 
> I'm presently integrating security measures, particularly focusing on hardening the application's base. After exploring FastAPI's capabilities, I'm integrating middleware for CORS headers and user-agent. I've also found a strong password hashing library to replace the current weaker method, enhancing the login system's security. Further, I'll integrate code vulnerability scans with `bandit` and dependency audits with `pip-audit` into the CI/CD pipeline for continual improvement.
> 
> **Enhancing Security Measures**
> 
> I'm presently integrating security measures, particularly focusing on hardening the application's base. After exploring FastAPI's capabilities, I'm integrating middleware for CORS headers and user-agent. I've also found a strong password hashing library to replace the current weaker method, enhancing the login system's security. Further, I'll integrate code vulnerability scans with `bandit` and dependency audits with `pip-audit` into the CI/CD pipeline for continual improvement.

¡Entendido! Vamos a pulir tu `config.py`, hablar de cómo ponerlo en producción en tu subdominio, revisar la seguridad y, lo más importante, añadir un historial de chat persistente con "memoria" para la IA.

Aquí tienes el análisis y las soluciones.

* * *

1\. Variables de Configuración (`config.py` y `.env`)
-----------------------------------------------------

Tu pregunta sobre `config.py` es excelente. Tienes dos formas de gestionar la configuración, y la mejor es usarlas juntas:

1.  **Tu Archivo `config.py`:** Es perfecto para variables _no secretas_ de la aplicación (como `INMO`, `PLANTILLA_PATH`, `OLLAMA_MODEL`, etc.). **Puedes añadir tantas variables como quieras aquí.**
2.  **Archivos `.env` (El estándar de Chainlit/Docker):** Es el lugar ideal para _secretos_ (como contraseñas de BBDD, claves de API, etc.). Tu `config.py` ya está preparado para leerlas con `os.environ.get()`.

**Mi recomendación:** Vamos a crear un archivo `.env` para el desarrollo local. Esto te permite tener contraseñas en tu PC sin subirlas a Git.

#### Nuevo Archivo: `.env`

(Crea este archivo en la misma carpeta que tu `docker-compose.yml`)

```
# Este archivo es para desarrollo local
# Docker Compose leerá estas variables y las pasará al contenedor

# Credenciales de MariaDB (coinciden con docker-compose.yml)
DB_HOST=mariadb
DB_USER=hogar_user
DB_PASS=hogar_pass
DB_NAME=hogar_familiar_db

# Aquí irían otros secretos, por ejemplo
# OLLAMA_API_KEY=tu_clave_secreta_si_la_tuvieras
```

No necesitas modificar `config.py`; ya está perfectamente configurado para leer estas variables.

* * *

2\. Puesta en Producción (Tu Subdominio `chat.jorgemc.casa`)
------------------------------------------------------------

Esto es un paso de **despliegue (producción)**, no un cambio en el código Python. Para que tus compañeros lo vean en `chat.jorgemc.casa`, necesitas 3 cosas:

1.  **Un Servidor (VPS):** Un servidor en la nube (como DigitalOcean, Vultr, Hetzner, etc.) con una IP pública fija.
2.  **DNS:** Configurar tu dominio `jorgemc.casa` para que el subdominio `chat` (un registro `A`) apunte a la IP de ese servidor.
3.  **Un Reverse Proxy:** Un servicio que reciba el tráfico web (puertos 80/443), gestione el **HTTPS (SSL) automáticamente** y redirija el tráfico a tu app de Chainlit (que corre en el puerto 8000).

El mejor para esto es **Traefik**, porque se integra directamente con Docker.

Aquí tienes un `docker-compose.yml` modificado **solo para producción** (no lo uses en local, o usa un archivo `docker-compose.prod.yml`):

#### `docker-compose.prod.yml` (Ejemplo para Producción)

```
version: '3.8'

services:
  app:
    build: .
    command: chainlit run app.py -w --port 8000 --host 0.0.0.0
    restart: unless-stopped
    volumes:
      - .:/app
    environment:
      # Pasas los secretos de la BBDD desde el servidor
      - DB_HOST=mariadb
      - DB_USER=${DB_USER} # Lee variables del entorno del servidor
      - DB_PASS=${DB_PASS}
      - DB_NAME=${DB_NAME}
    depends_on:
      - mariadb
    labels:
      # --- Configuración de Traefik ---
      - "traefik.enable=true"
      - "traefik.http.routers.chainlit.rule=Host(`chat.jorgemc.casa`)"
      - "traefik.http.routers.chainlit.entrypoints=websecure"
      - "traefik.http.services.chainlit.loadbalancer.server.port=8000"
      - "traefik.http.routers.chainlit.tls.certresolver=letsencrypt"

  mariadb:
    image: mariadb:10.6
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASS}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASS}
    volumes:
      - mariadb_data:/var/lib/mysql

  traefik:
    image: "traefik:v2.10"
    command:
      - "--api.insecure=true" # (Solo para debug, quítalo después)
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=tu-email@jorgemc.casa"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "traefik_certs:/letsencrypt"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"

volumes:
  mariadb_data:
  traefik_certs:
```

* * *

3\. Seguridad (Addons, Plugins y Prácticas)
-------------------------------------------

Basado en mi búsqueda, la seguridad de tu app se divide en 3 capas:

### Capa 1: Código (Python)

Tu app usa Chainlit, que se basa en el framework **FastAPI**. Esto significa que puedes usar las herramientas de seguridad de FastAPI.

*   **Herramientas de Análisis:**
    *   **`bandit`**: Es un linter que escanea tu código Python en busca de vulnerabilidades comunes (como `md5`, SQL injection, etc.).
    *   **`pip-audit`**: Escanea tus dependencias (`requirements.txt`) en busca de vulnerabilidades conocidas (CVEs).
*   **Prácticas Recomendadas:**
    *   **Hashing de Contraseñas:** `md5` (el que usas en `config.py`) se considera inseguro. Deberías migrar a una librería moderna como **`passlib`** (similar a `pwdlib` mencionado en los resultados) que usa algoritmos fuertes como **Argon2** o **Bcrypt**.
    *   **Manejo de PII:** Chainlit tiene guías específicas para asegurar que la Información Personal Identificable (PII) no se envíe accidentalmente a los modelos de lenguaje.

### Capa 2: Infraestructura (Docker)

Ya estás siguiendo buenas prácticas que encontré en mi búsqueda:

*   Usas una imagen base `-slim` (como la de tu `Dockerfile`).
*   Usas variables de entorno para los secretos (`os.environ`), lo cual es excelente.

### Capa 3: Red (Reverse Proxy)

Como mencioné en el punto 2, usar **Traefik** o **Nginx** es una práctica de seguridad fundamental. Te proporciona:

*   **HTTPS (SSL):** Cifra todo el tráfico entre tus usuarios y el servidor.
*   **Ocultación:** Tus usuarios nunca acceden al puerto `8000` de Chainlit directamente; solo ven el proxy.
*   **Rate Limiting:** (Avanzado) Puedes configurarlo para bloquear IPs que hagan demasiadas peticiones (protección contra ataques DoS).

* * *

4\. Historial de Chat y Memoria de IA (Código Corregido)
--------------------------------------------------------

Esto es clave para la usabilidad. Vamos a guardar cada mensaje en MariaDB y a usar ese historial para darle "memoria" a la IA en cada nueva consulta.

### `hfloudgemini/db.py` (Modificado)

(Añadimos la tabla `chat_history` y las funciones para guardar/cargar)

```
# db.py - MariaDB/MySQL
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_CONFIG
import json
import os # Añadido para leer variables de entorno

# Leemos las variables de entorno para la BBDD
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS', ''),
    'database': os.environ.get('DB_NAME', 'test_db')
}

def get_db_connection():
    """Crea y devuelve una conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_db_connection()
    if conn is None:
        print("Error: No se pudo conectar a la BBDD para inicializar.")
        return
    
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                usuario TEXT,
                fecha DATETIME,
                pdf_path TEXT,
                datos_json LONGTEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                contrato_id INTEGER,
                tipo TEXT,
                nombre_archivo TEXT,
                ruta TEXT,
                ocr_text LONGTEXT,
                fecha_subida DATETIME,
                FOREIGN KEY (contrato_id) REFERENCES contratos(id)
            )
        ''')
        # --- NUEVA TABLA PARA HISTORIAL DE CHAT ---
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                usuario TEXT,
                role ENUM('user', 'assistant'),
                content LONGTEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        print("Base de datos inicializada correctamente.")
    except Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn and conn.is_connected():
            c.close()
            conn.close()

def guardar_contrato(usuario, pdf_path, datos):
    """Guarda un nuevo contrato en la base de datos."""
    conn = get_db_connection()
    if conn is None: return None
    
    contrato_id = None
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO contratos (usuario, fecha, pdf_path, datos_json) VALUES (%s, %s, %s, %s)",
            (usuario, datetime.now(), pdf_path, datos)
        )
        conn.commit()
        contrato_id = c.lastrowid
    except Error as e:
        print(f"Error al guardar contrato: {e}")
    finally:
        if conn and conn.is_connected():
            c.close()
            conn.close()
    return contrato_id

def guardar_documento(contrato_id, tipo, nombre, ruta, ocr_text):
    """Guarda un documento asociado a un contrato."""
    conn = get_db_connection()
    if conn is None: return
        
    try:
        c = conn.cursor(buffered=True) # Usar buffered cursor
        
        # Primero, verificamos si el contrato_id existe
        c.execute("SELECT id FROM contratos WHERE id = %s", (contrato_id,))
        if c.fetchone() is None:
            # Si el contrato no existe (ej. al subir DNI antes de crearlo)
            # Podríamos crear un contrato 'temporal' o manejarlo.
            # Por ahora, simplemente no lo insertamos si el ID de contrato no es válido.
            # O mejor, permitimos un ID de contrato temporal
            print(f"Advertencia: Contrato ID {contrato_id} no encontrado. Se guardará el documento igualmente.")
            # O podemos decidir no guardar:
            # print(f"Error: Contrato ID {contrato_id} no existe. No se puede guardar el documento.")
            # return 
            pass # Continuamos para guardarlo de todas formas

        c.execute(
            "INSERT INTO documentos (contrato_id, tipo, nombre_archivo, ruta, ocr_text, fecha_subida) VALUES (%s, %s, %s, %s, %s, %s)",
            (contrato_id, tipo, nombre, ruta, ocr_text, datetime.now())
        )
        conn.commit()
    except Error as e:
        print(f"Error al guardar documento: {e}")
    finally:
        if conn and conn.is_connected():
            c.close()
            conn.close()

# --- NUEVAS FUNCIONES DE CHAT ---

def guardar_mensaje_chat(usuario, role, content):
    """Guarda un único mensaje (de usuario o IA) en la BBDD."""
    conn = get_db_connection()
    if conn is None: return
        
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO chat_history (usuario, role, content, timestamp) VALUES (%s, %s, %s, %s)",
            (usuario, role, content, datetime.now())
        )
        conn.commit()
    except Error as e:
        print(f"Error al guardar mensaje de chat: {e}")
    finally:
        if conn and conn.is_connected():
            c.close()
            conn.close()

def cargar_historial_chat(usuario, limite=20):
    """Carga los últimos 'limite' mensajes de un usuario para dar contexto a la IA."""
    conn = get_db_connection()
    if conn is None: return []
    
    historial = []
    try:
        c = conn.cursor(dictionary=True) # Devuelve resultados como diccionarios
        c.execute(
            "SELECT role, content FROM chat_history WHERE usuario = %s ORDER BY timestamp DESC LIMIT %s",
            (usuario, limite)
        )
        # Los devolvemos en orden cronológico (el más antiguo primero)
        historial = list(reversed(c.fetchall()))
    except Error as e:
        print(f"Error al cargar historial de chat: {e}")
    finally:
        if conn and conn.is_connected():
            c.close()
            conn.close()
    
    # Formateamos para Ollama: [{'role': 'user', 'content': '...'}, ...]
    return historial
```

### `hfloudgemini/app.py` (Modificado)

(Lo modificamos para que guarde mensajes y cargue la "memoria")

```
# app.py - VERSIÓN CORREGIDA Y CON MEMORIA DE CHAT
import chainlit as cl
import ollama
import hashlib
import os
from datetime import datetime
from config import USERS, OUTPUT_DIR, DOCS_DIR, INMO, OLLAMA_MODEL 
from ocr_utils import procesar_dni
from pdf_utils import generar_pdf
# Importamos las NUEVAS funciones de BBDD
from db import init_db, guardar_contrato, guardar_documento, guardar_mensaje_chat, cargar_historial_chat
import json

# === INICIALIZACIÓN ===
init_db()

@cl.on_chat_start
async def start():
    # CONFIGURACIÓN DE PÁGINA AL INICIO
    cl.set_page_config(
        title="Hogar Familiar | Asistente Legal IA",
        description="Contratos, OCR, IA legal actualizada",
        favicon="public/favicon.ico"
    )

    # Login
    if not cl.user_session.get("logged_in"):
        await login_flow()
        if not cl.user_session.get("logged_in"): # Si el login falla o se cancela
             await cl.Message(content="Debes iniciar sesión para continuar.").send()
             return

    # Saludo personalizado
    user = cl.user_session.get("username", "Usuario").capitalize()
    hora = datetime.now().hour
    saludo = "¡Buenos días" if 5 <= hora < 12 else "¡Buenas tardes" if hora < 20 else "¡Buenas noches"
    
    # --- MOSTRAR HISTORIAL DE CHAT ANTERIOR ---
    historial_db = cargar_historial_chat(user)
    # Guardamos el historial en la sesión para usarlo como "memoria"
    cl.user_session.set("chat_history", historial_db) 
    
    if historial_db:
        await cl.Message(content=f"--- Cargando tu historial reciente ---").send()
        for msg in historial_db:
            await cl.Message(
                content=msg['content'],
                author=msg['role'].capitalize() # 'user' o 'assistant'
            ).send()
        await cl.Message(content=f"--- Fin del historial ---").send()

    await cl.Message(content=f"{saludo}, **{user}**! ¿En qué te ayudo hoy?").send()

    # Footer legal
    await cl.run_js("""
    setTimeout(() => {
      let footer = document.getElementById('app-footer');
      if (!footer) {
        footer = document.createElement('div');
        footer.id = 'app-footer';
        footer.style.cssText = 'text-align:center; font-size:11px; color:#888; margin:20px 0; line-height:1.4;';
        document.body.appendChild(footer);
      }
      footer.innerHTML = `
        <strong>Sistema Privado</strong> • Solo para personal y clientes de
        <strong>Hogar Familiar Inmobiliaria</strong> (CIF B-01755321).<br>
        <a href="/legal.html" style="color:#1a73e8;">Ver términos legales</a>
      `;
    }, 500);
    """)

async def login_flow():
    await cl.Message(content="Inicia sesión para continuar").send()
    user_resp = await cl.AskUserMessage(content="Usuario:", timeout=60).send()
    if not user_resp: return
    
    username = user_resp["content"].strip().lower()
    if username not in USERS:
        await cl.Message(content="Usuario incorrecto").send()
        return await login_flow() # Bucle hasta login correcto
        
    pass_resp = await cl.AskUserMessage(content="Contraseña:", password=True, timeout=60).send()
    if not pass_resp: return

    password = pass_resp["content"]
    if hashlib.md5(password.encode()).hexdigest() != USERS[username]:
        await cl.Message(content="Contraseña incorrecta").send()
        return await login_flow() # Bucle
        
    cl.user_session.set("logged_in", True)
    cl.user_session.set("username", username)
    await cl.Message(content="Login correcto").send()

@cl.on_message
async def main(msg: cl.Message):
    if not cl.user_session.get("logged_in"):
        await cl.Message(content="Tu sesión ha expirado. Por favor, refresca la página para iniciar sesión.").send()
        return

    s = cl.user_session
    username = s.get("username", "usuario")
    
    # Cargamos la "memoria" de la IA
    chat_history = s.get("chat_history", [])

    # === SUBIDA DE DOCUMENTOS ===
    if msg.elements:
        await cl.Message(content="Procesando documento(s)...").send()
        docs = s.get("documentos", [])
        for el in msg.elements:
            if el.type == "image":
                es_anverso = len([d for d in docs if "anverso" in d.get("ruta", "")]) == 0
                data = procesar_dni(el.path, es_anverso)
                docs.append(data)
                await cl.Message(content=f"Detectado: **{data['nombre']}** (DNI: {data['dni']})").send()
                
                # --- GUARDAR DOCUMENTO ---
                # Usamos un ID temporal si el contrato no se ha creado
                # El flujo de 'generar_contrato_flow' lo actualizará luego
                contrato_id = s.get("contrato_id", None)
                if contrato_id:
                     guardar_documento(contrato_id, "DNI", os.path.basename(data["ruta"]), data["ruta"], data["ocr"])
                else:
                    # Opcional: guardarlo con un ID nulo o temporal si quieres
                    print("Documento subido pero contrato_id aún no existe.")
                    
        s.set("documentos", docs)
        return # No procesar texto si hay archivos

    # === COMANDOS DE TEXTO ===
    
    # --- Guardar mensaje de usuario ---
    text = msg.content.lower().strip()
    guardar_mensaje_chat(username, "user", msg.content) # Guardamos el mensaje original, no 'text' en minúsculas
    chat_history.append({"role": "user", "content": msg.content})

    if "generar contrato" in text:
        await generar_contrato_flow(s, username)
        # Limpiamos la memoria para que el siguiente chat no se confunda con los datos del contrato
        s.set("chat_history", []) 

    elif text in ["ya está", "finalizar", "generar pdf"]:
        if s.get("documentos"):
            await generar_pdf_documentos(s, username)
        else:
            await cl.Message(content="No hay documentos subidos.").send()

    else:
        # --- Llamada a IA con MEMORIA ---
        # Añadimos el mensaje actual al historial de la sesión
        messages_for_ia = chat_history
        
        try:
            respuesta_msg = cl.Message(content="") # Preparamos un mensaje vacío para el streaming
            await respuesta_msg.send()

            stream = await ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages_for_ia,
                stream=True
            )
            
            respuesta_completa = ""
            async for chunk in stream:
                if chunk['message']['content']:
                    respuesta_completa += chunk['message']['content']
                    await respuesta_msg.stream_token(chunk['message']['content'])

            await respuesta_msg.update() # Finalizamos el mensaje

            # --- Guardar respuesta de IA ---
            guardar_mensaje_chat(username, "assistant", respuesta_completa)
            chat_history.append({"role": "assistant", "content": respuesta_completa})
            s.set("chat_history", chat_history) # Actualizamos la memoria de la sesión
            
        except Exception as e:
            await cl.Message(content=f"Error con IA. Prueba de nuevo. ({e})").send()

async def generar_contrato_flow(s, username):
    docs = s.get("documentos", [])
    if not docs:
        await cl.Message(content="Primero sube los DNIs.").send()
        return

    # Preguntas
    lugar_resp = await cl.AskUserMessage(content="Lugar de firma (ej: Los Santos de la Humosa):").send()
    direccion_resp = await cl.AskUserMessage(content="Dirección del inmueble:").send()
    precio_resp = await cl.AskUserMessage(content="Precio de venta (€):").send()
    honorarios_resp = await cl.AskUserMessage(content="Honorarios (€ IVA excl.):").send()
    exclusividad_resp = await cl.AskUserMessage(content="Exclusividad (sí/no):").send()
    meses_resp = await cl.AskUserMessage(content="Duración (meses):").send()
    jurisdiccion_resp = await cl.AskUserMessage(content="Jurisdicción:").send()

    lugar = lugar_resp['content'].strip()
    direccion = direccion_resp['content'].strip()
    
    # Construir datos
    lista = [f"D. {d['nombre']}, DNI {d['dni']}, domicilio en {direccion}" for d in docs]
    datos = {
        "LUGAR": lugar,
        "LISTA_VENDEDORES": " y ".join(lista),
        "ES_SON": "es" if len(docs) == 1 else "son",
        "DIRECCION_INMUEBLE": direccion,
        "PRECIO_VENTA": precio_resp['content'].strip(),
        "HONORARIOS": honorarios_resp['content'].strip(),
        "EXCLUSIVIDAD": exclusividad_resp['content'].strip().title(),
        "DURACION_MES": meses_resp['content'].strip(),
        "JURISDICCIÓN": jurisdiccion_resp['content'].strip(),
        "FIRMAS_VENDEDORES": "\n".join([f"[Firma {i+1}]" for i in range(len(docs))])
    }

    # Generar PDF
    pdf_name = f"intermediacion_{username}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
    generar_pdf(datos, pdf_path, username)

    # --- Guardar en DB y actualizar documentos ---
    contrato_id = guardar_contrato(username, pdf_path, json.dumps(datos))
    
    if contrato_id:
        s.set("contrato_id", contrato_id)
        # Ahora actualizamos los documentos que subimos antes
        for doc in docs:
            guardar_documento(contrato_id, "DNI", os.path.basename(doc["ruta"]), doc["ruta"], doc["ocr"])
    else:
        await cl.Message(content="Error: No se pudo guardar el contrato en la BBDD.").send()
        return

    await cl.Message(
        content="Contrato generado",
        elements=[cl.File(path=pdf_path, name=pdf_name)]
    ).send()
    s.set("documentos", []) # Limpiar documentos después de generar

async def generar_pdf_documentos(s, username):
    docs = s.get("documentos", [])
    if not docs:
        await cl.Message(content="No hay documentos.").send()
        return

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    pdf_path = os.path.join(OUTPUT_DIR, f"documentos_{username}_{datetime.now():%Y%m%d_%H%M%S}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 50

    for doc in docs:
        c.drawString(50, y, f"DNI: {doc['dni']} - {doc['nombre']}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()

    await cl.Message(content="PDF de documentos generado", elements=[cl.File(path=pdf_path)]).send()
```



---
Powered by [Gemini Exporter](https://www.geminiexporter.com)