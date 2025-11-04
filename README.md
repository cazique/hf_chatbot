# ImmoDoc OCR

ImmoDoc OCR es una aplicación de gestión documental para inmobiliarias
con capacidades de OCR (reconocimiento óptico de caracteres) y
optimización de archivos PDF.  Este proyecto incluye una integración
modular con proveedores de modelos de lenguaje (LLM) que permite
configurar y cambiar el proveedor de IA sin modificar el código
principal.

El diseño de la interfaz de administración se ha inspirado en plantillas
modernas de paneles, utilizando **Tailwind CSS** junto con la
biblioteca de componentes **Flowbite**.  Esto permite contar con un
menú lateral navegable, tarjetas de estadísticas y elementos
interactivos (menús desplegables, modales, etc.) sin depender de
servicios externos.  Todos los recursos se cargan desde CDNs públicos
y pueden ser autohospedados en el directorio `static/` si así se
desea.

## Configuración de Proveedores de IA

La aplicación utiliza un archivo JSON (`ai_config.json`) para
almacenar la lista de proveedores configurados y seleccionar cuál es
el activo.  El proveedor activo se utiliza para todas las llamadas
relacionadas con modelos de lenguaje.  La configuración se monta en
el contenedor Docker mediante un volumen, lo que permite modificarla
sin reconstruir la imagen.

El formato del archivo es el siguiente:

```json
{
  "default_provider": "ollama_cloud_default",
  "providers": [
    {
      "id": "ollama_cloud_default",
      "name": "Ollama Cloud (Default)",
      "type": "ollama",
      "api_key": "TU_API_KEY",
      "base_url": "https://ollama.com",
      "model": "gpt-oss:20b-cloud"
    }
  ]
}
```

Donde:

- **id**: un identificador único para cada proveedor.  Se genera
  automáticamente al añadir uno nuevo desde el panel de administración.
- **name**: nombre legible que se mostrará en la interfaz de
  administración.
- **type**: tipo de proveedor (`ollama`, `openai`, `anthropic`, etc.).
- **api_key**: clave de autenticación.  Ollama Cloud y otros
  servicios requieren una API key para poder utilizar el modelo.
- **base_url**: URL base del servicio.  Para Ollama Cloud normalmente
  es `https://ollama.com`.  Si utiliza un despliegue de Ollama
  autohospedado, indique la URL de su instancia.
- **model**: nombre del modelo a utilizar por defecto.  Ollama Cloud
  proporciona varios modelos; puede consultar su documentación para
  elegir uno adecuado.

### Añadir y gestionar proveedores

Desde la interfaz de administración (`/admin/config`) un usuario con
permisos de administrador puede:

1. Visualizar los proveedores configurados y ver cuál está activo.
2. Activar un proveedor diferente.
3. Eliminar proveedores existentes.
4. Añadir nuevos proveedores indicando nombre, tipo, clave, modelo y
   URL base.
5. Probar la conexión de un proveedor para verificar que las
   credenciales y la URL son correctas.

Las acciones anteriores se realizan a través de llamadas a los
siguientes endpoints:

| Método | Endpoint                                     | Descripción                                     |
|-------|----------------------------------------------|------------------------------------------------|
| POST  | `/admin/api/providers/add`                   | Añade un proveedor.  Recibe JSON con `name`, `type`, `api_key`, `base_url` y `model`. |
| POST  | `/admin/api/providers/activate/<provider_id>` | Activa el proveedor cuyo `id` se especifica. |
| DELETE| `/admin/api/providers/delete/<provider_id>`   | Elimina el proveedor indicado. |
| GET   | `/admin/api/providers/test/<provider_id>`     | Prueba la conexión del proveedor indicado. |

### Configuración de Ollama Cloud

Ollama Cloud es el proveedor por defecto.  Para configurarlo:

1. Cree una cuenta en [Ollama](https://ollama.com) y solicite acceso
   a **Ollama Cloud**.
2. Obtenga su **API key** desde el panel de usuario de Ollama.
3. Edite el archivo `ai_config.json` y sustituya el valor de
   `YOUR_API_KEY` por su clave real.
4. Asegúrese de que el archivo `ai_config.json` se monta en el
   contenedor Docker a través del volumen configurado en
   `docker-compose.yml`.

Una vez configurado, el proveedor `Ollama Cloud` estará listo para
generar respuestas mediante el endpoint `/api/generate` tal y como se
detalla en la [documentación oficial de Ollama Cloud](https://docs.ollama.com/cloud).

## Puesta en marcha

1. Asegúrese de tener instalados Docker y Docker Compose.
2. Clone el repositorio y sitúese en el directorio del proyecto.
3. Cree (o edite) el archivo `ai_config.json` en la raíz siguiendo el
   formato mencionado arriba.
4. Cree el directorio `db` en la raíz del proyecto (si no existe).
   Este directorio se utilizará para almacenar las bases de datos
   SQLite (`users.db` y `ocr_logs.db`).  Al montar una carpeta en
   lugar de archivos individuales se evita el problema de que Docker
   genere directorios en lugar de ficheros cuando estos no existen,
   lo cual provoca errores al abrir las bases de datos.
5. Ejecute `docker-compose up --build` para levantar los servicios.
6. Acceda a la aplicación en `http://localhost:5000` y utilice las
   credenciales por defecto (`admin`/`admin`) para iniciar sesión.
7. Acceda a `/admin/config` para gestionar los proveedores de IA.

**Nota:** No ejecutes la aplicación local ni el script `run_local.sh`
con `sudo`.  Usar `sudo` crea los archivos de base de datos con
permisos de superusuario, impidiendo que la aplicación los modifique y
provocando errores como *«attempt to write a readonly database»*.  Si
ya ejecutaste el script con `sudo`, elimina el directorio `db/` y
ejecuta de nuevo `run_local.sh` sin privilegios de administrador.

### Ejecución local sin Docker

Si desea ejecutar la aplicación en un entorno local (sin contenedores),
puede utilizar el script proporcionado `run_local.sh` que prepara un
entorno virtual e instala las dependencias.  Simplemente ejecute:

```bash
chmod +x run_local.sh
./run_local.sh
```

El script creará un entorno virtual en el directorio `.venv`,
instalará las dependencias listadas en `requirements.txt` y lanzará
automáticamente la aplicación Flask.  Asegúrese de tener Python
3.10+ instalado en su sistema.

## Notas de desarrollo

Los módulos bajo `services/` son implementaciones mínimas para
mantener funcional el backend durante la refactorización.  Deben
reemplazarse por versiones completas que integren librerías como
Tesseract, Ghostscript, pdfminer, etc.  Asimismo, la clase
`OllamaCloudProvider` implementada en `ia_providers.py` muestra cómo
comunicarse con la API REST de Ollama; futuros proveedores deben
seguir esta interfaz heredando de `LLMProvider`.