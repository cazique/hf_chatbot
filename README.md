# Chatbot Legal Inmobiliario - HOGAR FELIZ REAL ESTATE

Este proyecto implementa un chatbot avanzado diseñado para asistir a los agentes de HOGAR FELIZ REAL ESTATE en la creación y gestión de contratos de intermediación inmobiliaria. El sistema está construido para un entorno de producción, priorizando la seguridad, escalabilidad y una integración fluida con los sistemas existentes de la empresa.

## Stack Tecnológico

-   **Backend & Interfaz de Chat**: [Chainlit](https://docs.chainlit.io/overview)
-   **Modelo de Lenguaje (IA)**: Integrado con [Ollama](https://ollama.com/) (compatible con modelos como Llama 3, Mixtral, etc.)
-   **Base de Datos**: [MariaDB 10.6](https://mariadb.org/)
-   **Autenticación**: Single Sign-On (SSO) mediante [JSON Web Tokens (JWT)](https://jwt.io/), compatible con proveedores de identidad como WordPress o AppGini.
-   **Procesamiento de Documentos**: [OpenCV](https://opencv.org/) y [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) para el escaneo y procesamiento de DNI y otros documentos.
-   **Contenerización**: [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/)
-   **Exposición Segura a Internet**: [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/)

## Características Principales

-   **Autenticación Segura (SSO)**: Los usuarios no se registran en el chatbot. El acceso se concede a través de un portal externo (ej. WordPress) que genera un JWT, garantizando un único punto de entrada.
-   **Gestión de Historial**: Todas las conversaciones se guardan en la base de datos, permitiendo a los usuarios continuar sus sesiones y a los administradores auditar las interacciones.
-   **Procesamiento OCR de Documentos**: Los agentes pueden subir imágenes (DNI, notas simples) que son procesadas para extraer información y adjuntarlas a los contratos.
-   **Generación de Documentos PDF**: El sistema puede generar contratos en PDF a partir de plantillas y los datos proporcionados durante la conversación.
-   **Memoria Conversacional**: El chatbot recuerda el contexto de la conversación actual para ofrecer respuestas más coherentes y precisas.
-   **Listo para Producción**: Desplegado con Docker y securizado a través de Cloudflare, con toda la configuración gestionada mediante variables de entorno.

## Configuración del Entorno

Para ejecutar el proyecto, es necesario crear un archivo `.env` en la raíz del proyecto. Puedes usar el archivo `.env.example` como plantilla.

```bash
cp .env.example .env
```

A continuación, edita el archivo `.env` con tus propios valores:

-   `DB_ROOT_PASSWORD`, `DB_NAME`, `DB_USER`, `DB_PASS`: Credenciales para la base de datos MariaDB.
-   `OLLAMA_API_KEY`, `OLLAMA_BASE_URL`: Credenciales y URL para tu instancia de Ollama (si es necesario).
-   `CLOUDFLARE_TUNNEL_TOKEN`: El token de tu túnel de Cloudflare para exponer el servicio de forma segura.
-   `JWT_PUBLIC_KEY`: La **clave pública** en formato PEM que se usará para verificar la firma de los tokens JWT generados por tu sistema de autenticación.
-   `JWT_ALGORITHM`: El algoritmo de firma (ej. `RS256`).

### Nota sobre JWT_PUBLIC_KEY

La clave pública debe tener el formato exacto, incluyendo los saltos de línea `\n`. Ejemplo:

```
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAyour_public_key_here\n... (más líneas) ...\n-----END PUBLIC KEY-----"
```

## Ejecución

Una vez configurado el archivo `.env`, puedes levantar todo el stack con un solo comando:

```bash
docker-compose up -d
```

Los servicios que se iniciarán son:

1.  **db**: El contenedor de la base de datos MariaDB.
2.  **app**: El contenedor de la aplicación Chainlit.
3.  **cloudflared**: El contenedor que crea el túnel seguro a Cloudflare.

La aplicación estará disponible en el puerto `8000` del host local y, si el túnel de Cloudflare está bien configurado, a través de la URL pública que hayas definido.
