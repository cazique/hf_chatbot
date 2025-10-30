# Hogar Feliz Chatbot - Asistente de Contratos Inmobiliarios

Este proyecto es un chatbot avanzado diseñado para asistir a los agentes de la inmobiliaria "Hogar Feliz" en la creación y gestión de borradores de contratos de alquiler. La aplicación está construida con Chainlit, utiliza modelos de lenguaje de Ollama, y está completamente dockerizada para un despliegue sencillo y robusto.

## Características Principales

- **Autenticación Segura:** Sistema de login basado en JWT para proteger el acceso a la aplicación.
- **Interfaz de Chat Inteligente:** Interfaz conversacional fluida gracias a Chainlit para interactuar con el asistente.
- **Soporte Multi-IA:** Permite configurar y seleccionar en tiempo real diferentes proveedores de modelos de lenguaje (locales o en la nube) a través de Ollama.
- **Procesamiento Avanzado de Documentos (OCR):**
  - Sube imágenes de documentos (DNI, pasaportes, etc.).
  - **Corrección de Orientación:** Detecta y rota automáticamente las imágenes.
  - **Recorte de Perspectiva:** Transforma la imagen para darle un aspecto "escaneado", aislando el documento del fondo.
  - Extracción de texto precisa con Tesseract.
- **Panel de Administración:** Los usuarios marcados como `is_admin` tienen acceso a comandos especiales, como `/admin_users` para listar todos los usuarios del sistema.
- **Base de Datos Persistente:** Utiliza MariaDB (MySQL) para almacenar usuarios y historiales de chat, asegurando que las conversaciones se guarden entre sesiones.
- **Generación de Documentos PDF:** Crea un borrador del contrato en formato PDF al final de la conversación, incluyendo el historial del chat y las imágenes procesadas de los documentos.
- **Contexto Legal Integrado:** El chatbot está enriquecido con información clave de la Ley de Arrendamientos Urbanos (LAU) de España para generar contratos más precisos.
- **Despliegue Sencillo con Docker:** Totalmente contenedorizado con `docker-compose`, facilitando el despliegue en cualquier entorno.
- **Túnel Seguro (Opcional):** Integración con Cloudflare Tunnel para exponer la aplicación de forma segura a internet.

## Arquitectura

El sistema se compone de tres servicios principales orquestados por Docker Compose:

1.  **`app`:** El contenedor principal que ejecuta la aplicación Chainlit en Python. Se encarga de la lógica de negocio, la interacción con el LLM, el OCR y la generación de PDF.
2.  **`db`:** Un contenedor MariaDB que proporciona la base de datos persistente para usuarios e historiales de chat.
3.  **`cloudflared`:** (Opcional) Un contenedor que crea un túnel seguro con Cloudflare para exponer la aplicación a internet sin necesidad de abrir puertos.

## Cómo Empezar

### Prerrequisitos

- Docker y Docker Compose instalados.
- Git para clonar el repositorio.
- Una cuenta de Cloudflare y un token de túnel si deseas acceso externo (opcional).

### Pasos de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd hf_chatbot
    ```

2.  **Configurar el entorno:**
    Copia el archivo de ejemplo `.env.example` a `.env` y personaliza las variables.
    ```bash
    cp .env.example .env
    ```
    Edita el archivo `.env` con tu editor preferido:
    - `SECRET_KEY`: Una clave secreta larga y aleatoria para los JWT.
    - `OLLAMA_PROVIDERS`: Configura tus puntos de acceso a Ollama. El formato es `"Nombre|URL|Clave,..."`.
    - `MARIADB_*`: Contraseñas y nombres para la base de datos.
    - `CLOUDFLARE_TUNNEL_TOKEN`: (Opcional) Tu token de Cloudflare Tunnel.

3.  **Construir y ejecutar los contenedores:**
    Este comando construirá la imagen de la aplicación, descargará la de MariaDB y las iniciará en segundo plano.
    ```bash
    sudo docker compose up -d --build
    ```

4.  **Acceder a la aplicación:**
    - **Localmente:** Abre tu navegador y ve a `http://localhost:8000`.
    - **A través de Cloudflare:** Accede a la URL que te proporcionó Cloudflare para tu túnel.

5.  **Crear un usuario (Primer uso):**
    La primera vez, necesitarás crear un usuario en la base de datos para poder iniciar sesión. Puedes hacerlo conectándote a la base de datos directamente o mediante un script de inicialización. *(Instrucciones para crear un usuario administrador se añadirán en futuras versiones).*

## Uso de la Aplicación

1.  **Inicio de Sesión:** Al acceder, la aplicación te pedirá tu nombre de usuario y contraseña.
2.  **Selección de IA:** Elige con qué proveedor de modelo de lenguaje quieres trabajar en esta sesión.
3.  **Conversación:** Describe los detalles del contrato que necesitas. Puedes subir imágenes de documentos arrastrándolas al chat.
4.  **Comandos de Admin:** Si eres administrador, escribe `/admin_users` para ver la lista de usuarios.
5.  **Generación de Contrato:** Cuando tengas toda la información, indica al bot "genera el contrato" o "ya está todo" para recibir el PDF.

## Estructura del Proyecto

```
/
├── .env.example          # Plantilla para variables de entorno
├── app.py                # Lógica principal de la aplicación Chainlit
├── auth.py               # Funciones de autenticación (JWT, login)
├── config.py             # Carga y gestión de la configuración
├── db.py                 # Interacción con la base de datos MariaDB
├── ocr_utils.py          # Lógica para el procesamiento OCR avanzado
├── pdf_utils.py          # Utilidades para la creación de PDFs con ReportLab
├── legal.py              # Provee contexto legal sobre alquileres
├── legal.html            # Plantilla HTML para mostrar el contexto legal
├── Dockerfile            # Define el contenedor de la aplicación Python
├── docker-compose.yml    # Orquesta los servicios (app, db, cloudflared)
├── requirements.txt      # Dependencias de Python
└── public/
    └── style.css         # (Opcional) Estilos CSS personalizados para Chainlit
```
