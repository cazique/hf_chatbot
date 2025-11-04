# app.py - ImmoDoc OCR Application (Versión Mejorada)
# Descripción: Gestión documental inmobiliaria con OCR, optimización, dashboard, chatbot y preparación para IA
# Autor: Refactorización completa con mejoras
# Features: Auth, tema oscuro/claro, responsive, Docker-ready, chatbot integration, Ollama-ready

"""Flask application entry point for ImmoDoc OCR.

This version of ``app.py`` includes an abstraction layer for AI
providers and endpoints to manage those providers through the admin
interface.  Providers can be configured via a JSON file and selected
at runtime without modifying business logic.  The file remains
backwards compatible with existing OCR and PDF functionality while
extending the admin UI with provider management features.
"""

import os
import tempfile
import shutil
# Removed unused import: json
from datetime import datetime
from uuid import uuid4
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
# BadRequest is no longer imported since it is unused
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 as sql
import logging

# Imports locales
from services.ocr_service import perform_ocr  # type: ignore
from services.optimize_service import optimize_pdf  # type: ignore
from services.check_deps import check_dependencies  # type: ignore
from services.pdf_actions import extract_text_from_pdf, convert_pdf_to_images  # type: ignore
from PIL import Image

# Import provider configuration and factory
from config_manager import ConfigManager, get_active_provider

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_change_in_prod_12345')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
# Límite de tamaño de carga (por defecto 200MB).  Puede sobrescribirse
# mediante la variable de entorno MAX_FILE_SIZE.  Se expresa en bytes.
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 200 * 1024 * 1024))
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['OLLAMA_API_URL'] = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Registrar filtros de plantilla personalizados
@app.template_filter('basename')
def basename_filter(value: str) -> str:
    """Extrae el nombre base de una ruta de archivo.

    Este filtro se utiliza en las plantillas para mostrar sólo el
    nombre del archivo sin la ruta completa.

    Parameters
    ----------
    value: str
        Ruta completa al archivo.

    Returns
    -------
    str
        Nombre del archivo extraído de la ruta.
    """
    return os.path.basename(value) if value else ''

 # Paths for SQLite databases are relative to a ``db`` folder within the
 # application root.  If the directory does not exist, it will be
 # created on start.  This allows us to mount a single folder in
 # Docker for persistence instead of individual database files.  See
 # ``docker-compose.yml`` for volume definitions.

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DB_DIR: str = os.path.join(BASE_DIR, 'db')
os.makedirs(DB_DIR, exist_ok=True)
USERS_DB_PATH: str = os.path.join(DB_DIR, 'users.db')
LOGS_DB_PATH: str = os.path.join(DB_DIR, 'ocr_logs.db')

# Initialize configuration manager for AI providers.
# The configuration file path can be overridden via the AI_CONFIG_PATH
# environment variable.  By default it resides at ``ai_config.json`` in
# the application root.
CONFIG_PATH = os.getenv('AI_CONFIG_PATH', 'ai_config.json')
config_manager = ConfigManager(CONFIG_PATH)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id: int, username: str, password_hash: str,
                 theme: str = 'auto', color_scheme: str = 'green') -> None:
        """Representa a un usuario autenticado.

        Parameters
        ----------
        user_id: int
            Identificador único del usuario.
        username: str
            Nombre de usuario.
        password_hash: str
            Contraseña en formato hash.
        theme: str, optional
            Preferencia de tema (por defecto 'auto').
        color_scheme: str, optional
            Esquema de color preferido (por defecto 'green').
        """
        # Use a non‑built‑in name to avoid shadowing Python's built‑in ``id``
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.theme = theme
        self.color_scheme = color_scheme


@login_manager.user_loader
def load_user(user_id: str):
    """Load a user from the users database.

    Parameters
    ----------
    user_id: str
        The primary key of the user in the ``users`` table.

    Returns
    -------
    Optional[User]
        An instance of :class:`User` if the user exists; otherwise
        ``None``.
    """
    conn = sql.connect(USERS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        theme = row[3] if len(row) > 3 else 'auto'
        color = row[4] if len(row) > 4 else 'green'
        return User(row[0], row[1], row[2], theme, color)
    return None


def init_users_db() -> None:
    """Initialise the users database.

    This helper creates a SQLite database at ``USERS_DB_PATH`` with a
    table called ``users`` containing the columns ``id``,
    ``username``, ``password_hash``, ``theme`` and ``color_scheme``.  If
    the table already exists, it is left unchanged.  If no users are
    present, a default ``admin`` user is inserted with password
    ``admin`` (hashed).
    """
    conn = sql.connect(USERS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        theme TEXT DEFAULT 'auto',
        color_scheme TEXT DEFAULT 'green'
    )''')

    if cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        hash_pw = generate_password_hash('admin')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', hash_pw))

    conn.commit()
    conn.close()


def init_logs_db() -> None:
    """Initialise the logs database.

    Creates a SQLite database at ``LOGS_DB_PATH`` with a table
    ``logs`` used to record information about processed documents.
    The table is created if it does not exist; otherwise it is
    reused.
    """
    conn = sql.connect(LOGS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY,
        input_path TEXT,
        output_path TEXT,
        original_size INTEGER,
        new_size INTEGER,
        timestamp TEXT,
        mode TEXT,
        action TEXT,
        user_id INTEGER
    )''')
    conn.commit()
    conn.close()


def init_app():
    """Inicialización completa de la aplicación"""
    # Asegurar que las carpetas de bases de datos y subidas existen
    # antes de inicializar las bases.  Esto evita que SQLite cree
    # directorios con permisos inesperados y que el almacenamiento de
    # archivos dé errores por rutas inexistentes.
    try:
        os.makedirs(os.path.dirname(USERS_DB_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(LOGS_DB_PATH), exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as mkdir_err:  # noqa: BLE001
        logger.error(f'No se pudieron crear directorios iniciales: {mkdir_err}')

    init_users_db()
    init_logs_db()
    deps_status = check_dependencies()

    if not all(deps_status.values()):
        for tool, status in deps_status.items():
            if not status:
                logger.warning(f'{tool} no está disponible')


# ============= RUTAS DE AUTENTICACIÓN =============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use the configured path for the users database
        conn = sql.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[2], password):
            theme = row[3] if len(row) > 3 else 'auto'
            color = row[4] if len(row) > 4 else 'green'
            user = User(row[0], row[1], row[2], theme, color)
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Credenciales inválidas', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ============= RUTAS PRINCIPALES =============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con estadísticas"""
    # Use the configured path for the logs database
    conn = sql.connect(LOGS_DB_PATH)
    cursor = conn.cursor()

    # Documentos recientes
    cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10')
    docs = cursor.fetchall()

    # Estadísticas
    cursor.execute('SELECT COUNT(*) FROM logs')
    total_docs = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(original_size - new_size) FROM logs WHERE new_size < original_size')
    space_saved = cursor.fetchone()[0] or 0

    conn.close()

    return render_template('dashboard.html',
                         docs=docs,
                         total_docs=total_docs,
                         space_saved=space_saved)


@app.route('/logs')
@login_required
def view_logs():
    """Mostrar el historial de documentos procesados.

    Recupera las entradas de la base de datos de logs y las pasa a
    una plantilla que muestra información como archivo original,
    archivo procesado, tamaños y fechas.  Sólo usuarios
    autenticados pueden acceder a esta vista.
    """
    conn = sql.connect(LOGS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, input_path, output_path, original_size, new_size, timestamp, mode, action FROM logs ORDER BY timestamp DESC LIMIT 100')
    logs = cursor.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs)


@app.route('/features')
@login_required
def features_page():
    """Mostrar la página de características principales.

    Esta ruta renderiza una lista de funcionalidades destacadas del
    sistema.  Se protege con autenticación para mantener la
    información interna accesible sólo a usuarios registrados.
    """
    return render_template('features.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Página de subida de documentos"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'single':
            return process_single(request)
        elif action == 'batch':
            return process_batch(request)
        elif action == 'chatbot':
            return process_chatbot(request)

    return render_template('upload.html')


# ============= API PARA CHATBOT =============

@app.route('/api/chatbot/upload', methods=['POST'])
@login_required
def api_chatbot_upload():
    """API endpoint para chatbot - recibe PDF y retorna opciones o ejecuta acción"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        intent = request.form.get('intent', 'options')  # options, ocr, extract, convert

        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400

        # Guardar archivo temporal
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'chatbot_{filename}')
        file.save(filepath)

        # Según el intent, ejecutar acción
        if intent == 'options':
            # Retornar opciones disponibles
            return jsonify({
                'file_saved': filepath,
                'options': [
                    {'id': 'ocr', 'name': 'Hacer OCR', 'description': 'Extraer texto del PDF escaneado'},
                    {'id': 'extract', 'name': 'Extraer Texto', 'description': 'Obtener texto existente'},
                    {'id': 'optimize', 'name': 'Optimizar', 'description': 'Reducir tamaño del PDF'},
                    {'id': 'convert', 'name': 'Convertir a Imágenes', 'description': 'Extraer páginas como imágenes'}
                ]
            })

        elif intent == 'ocr':
            result = perform_ocr(filepath, lang='spa', deskew=True)
            if result['success']:
                log_process(filepath, result['output_path'], 'chatbot', 'ocr')
                return jsonify({
                    'success': True,
                    'output_file': result['output_path'],
                    'message': 'OCR completado exitosamente'
                })
            else:
                return jsonify({'error': result['error']}), 500

        elif intent == 'extract':
            text = extract_text_from_pdf(filepath)
            return jsonify({
                'success': True,
                'text': text,
                'message': 'Texto extraído exitosamente'
            })

        elif intent == 'optimize':
            result = optimize_pdf(filepath)
            if result['success']:
                log_process(filepath, result['output_path'], 'chatbot', 'optimize')
                return jsonify({
                    'success': True,
                    'output_file': result['output_path'],
                    'message': 'PDF optimizado exitosamente'
                })
            else:
                return jsonify({'error': result['error']}), 500

        elif intent == 'convert':
            images = convert_pdf_to_images(filepath)
            return jsonify({
                'success': True,
                'images': images,
                'message': f'{len(images)} imágenes extraídas'
            })

    except Exception as e:
        logger.error(f'Chatbot API error: {str(e)}')
        return jsonify({'error': str(e)}), 500


# ============= PROCESAMIENTO DE ARCHIVOS =============

def process_single(req):
    """Procesar un único PDF.

    El parámetro ``req`` corresponde al objeto ``flask.request`` que
    contiene los datos del formulario y los archivos subidos.  Se
    renombró para evitar sombrear la importación global ``request``.
    """
    filepath: str | None = None
    try:
        if 'file' not in req.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('upload'))

        file = req.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash('Archivo inválido', 'error')
            return redirect(url_for('upload'))

        # Verificar tamaño
        file.seek(0, os.SEEK_END)
        size = file.tell()
        if size > app.config['MAX_CONTENT_LENGTH']:
            flash('Archivo demasiado grande (máx. 100MB)', 'error')
            return redirect(url_for('upload'))
        file.seek(0)

        # Parámetros
        lang = req.form.get('language', 'spa')
        deskew = req.form.get('deskew') == 'on'
        optimize_flag = req.form.get('optimize') == 'on'

        # Guardar archivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Procesar OCR
        ocr_result = perform_ocr(filepath, lang=lang, deskew=deskew)
        if not ocr_result['success']:
            flash(f"Error en OCR: {ocr_result['error']}", 'error')
            return redirect(url_for('upload'))

        output_path = ocr_result['output_path']

        # Optimizar si se solicita
        if optimize_flag:
            opt_result = optimize_pdf(output_path)
            if opt_result['success']:
                os.unlink(output_path)
                output_path = opt_result['output_path']
            else:
                flash(f"Advertencia: No se pudo optimizar - {opt_result['error']}", 'warning')

        # Registrar en logs
        log_process(filepath, output_path, 'single', 'ocr')

        # Preparar archivo para descarga manual
        # Copiamos el archivo procesado a la carpeta de subidas con un nombre
        # legible para el usuario.  De este modo, Safari u otros navegadores
        # no intentarán descargar de inmediato un archivo que podría fallar
        # por permisos, y se ofrece un enlace en la página de resultado.
        processed_name = f"processed_{filename}"
        dest_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_name)
        try:
            # Copiar el archivo procesado a ``uploads`` si no está allí
            if output_path != dest_path:
                shutil.copyfile(output_path, dest_path)
        except Exception as copy_err:  # noqa: BLE001
            logger.error(f'No se pudo copiar el archivo procesado: {copy_err}')
            flash('Error al preparar el archivo procesado para descarga', 'error')
            return redirect(url_for('upload'))

        # Mostrar página de resultados con enlace de descarga
        download_url = url_for('download_processed', filename=processed_name)
        return render_template('upload_result.html', download_url=download_url, file_name=processed_name)

    except Exception as e:  # noqa: BLE001
        logger.error(f'Error procesando archivo: {str(e)}')
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('upload'))

    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.unlink(filepath)
            except Exception:
                pass


def process_batch(req):
    """Procesar múltiples PDFs.

    Acepta un objeto ``flask.request`` renombrado a ``req`` para evitar
    sombrear la importación global ``request``.
    """
    try:
        files = req.files.getlist('folder')

        if not files or all(f.filename == '' for f in files):
            flash('No se seleccionaron archivos', 'error')
            return redirect(url_for('upload'))

        # Parámetros
        lang = req.form.get('language', 'spa')
        deskew = req.form.get('deskew') == 'on'
        optimize_flag = req.form.get('optimize') == 'on'
        mode = int(req.form.get('mode', 2))

        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        pdf_paths: list[str] = []

        for file in files:
            if file and allowed_file(file.filename):
                # Verificar tamaño
                file.seek(0, os.SEEK_END)
                size = file.tell()
                file.seek(0)

                if size > app.config['MAX_CONTENT_LENGTH']:
                    flash(f'Archivo {file.filename} demasiado grande (ignorado)', 'warning')
                    continue

                # Guardar con estructura de carpetas
                rel_path = file.filename
                dir_path = os.path.join(temp_dir, os.path.dirname(rel_path))
                os.makedirs(dir_path, exist_ok=True)

                full_path = os.path.join(dir_path, os.path.basename(rel_path))
                file.save(full_path)

                if full_path.lower().endswith('.pdf'):
                    pdf_paths.append(full_path)

        if not pdf_paths:
            flash('No se encontraron archivos PDF válidos', 'error')
            shutil.rmtree(temp_dir)
            return redirect(url_for('upload'))

        # Procesar archivos
        # Inicializamos el diccionario de resultados con una lista vacía en ``details``.
        results: dict[str, object] = {'success': 0, 'errors': 0, 'details': []}

        for pdf in pdf_paths:
            try:
                ocr_result = perform_ocr(pdf, lang=lang, deskew=deskew)

                if ocr_result['success']:
                    output = ocr_result['output_path']

                    if optimize_flag:
                        opt_result = optimize_pdf(output)
                        if opt_result['success']:
                            os.unlink(output)
                            output = opt_result['output_path']

                    log_process(pdf, output, 'batch', f'mode_{mode}')
                    results['success'] = results.get('success', 0) + 1
                    # ``details`` está inicializado como una lista, por lo que append existe
                    details_list: list = results['details']  # type: ignore[assignment]
                    details_list.append({
                        'file': os.path.basename(pdf),
                        'status': 'success'
                    })
                else:
                    results['errors'] = results.get('errors', 0) + 1
                    details_list: list = results['details']  # type: ignore[assignment]
                    details_list.append({
                        'file': os.path.basename(pdf),
                        'status': 'error',
                        'error': ocr_result['error']
                    })

            except Exception as e:  # noqa: BLE001
                logger.error(f'Error procesando {pdf}: {str(e)}')
                results['errors'] = results.get('errors', 0) + 1
                details_list: list = results['details']  # type: ignore[assignment]
                details_list.append({
                    'file': os.path.basename(pdf),
                    'status': 'error',
                    'error': str(e)
                })

        shutil.rmtree(temp_dir)

        flash(f"Procesamiento completado: {results.get('success', 0)} exitosos, {results.get('errors', 0)} errores", 'info')
        return jsonify(results)

    except Exception as e:  # noqa: BLE001
        logger.error(f'Error en procesamiento batch: {str(e)}')
        flash(f'Error en procesamiento masivo: {str(e)}', 'error')
        return redirect(url_for('upload'))


def process_chatbot(req):
    """Procesar archivo desde chatbot con acción específica"""
    # Implementación similar a api_chatbot_upload pero desde formulario web
    pass


# ============= CHAT CON IA =============

@app.route('/chat')
@login_required
def chat():
    """Página de chat interactivo con IA.

    Permite enviar mensajes de texto y adjuntar archivos (PDF o imágenes)
    para que el modelo genere una respuesta contextualizada.  Si se
    adjuntan imágenes, se fusionan en un único PDF y se les aplica OCR.
    """
    return render_template('chat.html')


@app.route('/chat/api/send', methods=['POST'])
@login_required
def chat_send():
    """Procesar mensajes enviados desde el chat.

    Esta ruta espera un campo ``message`` con el texto del usuario y
    opcionalmente archivos enviados bajo el nombre ``files``.  Si los
    archivos son imágenes, se combinan en un PDF y se aplica OCR;
    si es un PDF, se extrae el texto con OCR.  Luego se llama al
    proveedor de IA activo con el prompt resultante y la pregunta del
    usuario.
    """
    user_text = request.form.get('message', '').strip()
    files = request.files.getlist('files')
    if not user_text and not files:
        return jsonify({'error': 'Debe escribir un mensaje o adjuntar un archivo'}), 400
    combined_text = ''
    # Procesar archivos adjuntos
    if files:
        pdf_paths: list[str] = []
        image_paths: list[str] = []
        for f in files:
            if f.filename == '':
                continue
            # Guardar cada archivo temporalmente
            filename = secure_filename(f.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"chat_{uuid4().hex}_{filename}")
            f.save(temp_path)
            if filename.lower().endswith('.pdf'):
                pdf_paths.append(temp_path)
            else:
                image_paths.append(temp_path)
        # Si hay imágenes, fusionarlas en un PDF
        if image_paths:
            merged_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"chat_images_{uuid4().hex}.pdf")
            try:
                merge_images_to_pdf(image_paths, merged_pdf_path)
                pdf_paths.append(merged_pdf_path)
            except Exception as merge_err:
                logger.error(f'No se pudieron fusionar las imágenes: {merge_err}')
            # Eliminar imágenes temporales
            for p in image_paths:
                try:
                    os.unlink(p)
                except Exception:
                    pass
        # Para cada PDF, extraer texto usando OCR
        for pdf in pdf_paths:
            try:
                ocr_result = perform_ocr(pdf, lang='spa', deskew=False)
                if ocr_result['success']:
                    with open(ocr_result['output_path'], 'r', encoding='utf-8', errors='ignore') as tf:
                        combined_text += tf.read() + '\n'
                else:
                    combined_text += ''
            except Exception as ocr_err:
                logger.error(f'OCR falló: {ocr_err}')
        # limpiar PDFs temporales
        for p in pdf_paths:
            try:
                os.unlink(p)
            except Exception:
                pass
    # Construir prompt para el modelo
    provider = get_active_provider(config_manager)
    if not provider:
        return jsonify({'error': 'No hay proveedor de IA activo'}), 500
    prompt = combined_text.strip()
    if prompt:
        prompt += f"\n\nPregunta del usuario: {user_text}"
    else:
        prompt = user_text
    try:
        ai_response = provider.generate_response(prompt)
        answer = ai_response.get('response') or ai_response.get('message') or str(ai_response)
    except Exception as err:
        logger.error(f'Error llamando al proveedor de IA: {err}')
        return jsonify({'error': 'No se pudo obtener respuesta del modelo'}), 500
    return jsonify({'response': answer})


def merge_images_to_pdf(image_paths: list[str], output_path: str) -> None:
    """Combinar varias imágenes en un único PDF.

    Parameters
    ----------
    image_paths: list[str]
        Rutas de las imágenes a fusionar.  Deben ser formatos soportados por
        Pillow (JPEG, PNG, etc.).
    output_path: str
        Ruta donde se guardará el PDF resultante.
    """
    if not image_paths:
        raise ValueError('No hay imágenes para combinar')
    images = []
    for path in image_paths:
        img = Image.open(path).convert('RGB')
        images.append(img)
    first_img, rest = images[0], images[1:]
    first_img.save(output_path, save_all=True, append_images=rest)


# =================== API UTILITARIA ===================

@app.route('/api/process', methods=['POST'])
def api_process_file():
    """Procesar archivos con diversas acciones.

    Esta API permite realizar varias operaciones sobre un archivo
    cargado, según el valor del parámetro ``action``.  Las acciones
    admitidas son:

    - ``ocr``: ejecutar OCR sobre el PDF y devolver el texto extraído.
    - ``optimize``: optimizar el PDF y devolver la ruta al nuevo
      archivo.
    - ``ocr_and_summarize``: extraer texto y pedir al proveedor de IA
      que lo resuma.
    - ``ocr_and_assign``: extraer texto, localizar un DNI mediante
      expresión regular y devolver el número encontrado.  Esta acción
      no realiza inserción en bases de datos; solo demuestra cómo
      detectar DNIs.

    El archivo debe enviarse en el campo ``file`` de ``multipart/form-data``.

    Returns
    -------
    Flask Response
        Objeto JSON con ``success`` y datos específicos de la acción.
    """
    action = request.form.get('action', '').strip().lower()
    upload = request.files.get('file')
    if not action or not upload:
        return jsonify({'success': False, 'error': 'Se requiere una acción y un archivo'}), 400
    # Guardar archivo temporal
    filename = secure_filename(upload.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"api_{uuid4().hex}_{filename}")
    upload.save(temp_path)
    try:
        if action == 'ocr':
            ocr_result = perform_ocr(temp_path, lang='spa', deskew=False)
            if ocr_result['success']:
                with open(ocr_result['output_path'], 'r', encoding='utf-8', errors='ignore') as tf:
                    text = tf.read()
                return jsonify({'success': True, 'text': text})
            return jsonify({'success': False, 'error': ocr_result.get('error', 'Error en OCR')})
        elif action == 'optimize':
            opt_result = optimize_pdf(temp_path)
            if opt_result['success']:
                processed_path = opt_result['output_path']
                filename = os.path.basename(processed_path)
                return jsonify({'success': True, 'file': f"/downloads/{filename}"})
            return jsonify({'success': False, 'error': opt_result.get('error', 'Error optimizando')})
        elif action == 'ocr_and_summarize':
            # OCR
            ocr_result = perform_ocr(temp_path, lang='spa', deskew=False)
            if not ocr_result['success']:
                return jsonify({'success': False, 'error': ocr_result.get('error', 'OCR falló')})
            with open(ocr_result['output_path'], 'r', encoding='utf-8', errors='ignore') as tf:
                text = tf.read()
            # Consultar proveedor de IA para resumir
            provider = get_active_provider(config_manager)
            if not provider:
                return jsonify({'success': False, 'error': 'No hay proveedor activo'})
            try:
                ai_response = provider.generate_response(
                    f"Resume el siguiente texto:\n{text[:3000]}"
                )
                summary = ai_response.get('response') or ai_response.get('message') or str(ai_response)
            except Exception as err:
                return jsonify({'success': False, 'error': f'Error llamando al proveedor: {err}'})
            return jsonify({'success': True, 'summary': summary, 'text': text})
        elif action == 'ocr_and_assign':
            import re
            # Extraer texto
            ocr_result = perform_ocr(temp_path, lang='spa', deskew=False)
            if not ocr_result['success']:
                return jsonify({'success': False, 'error': ocr_result.get('error', 'OCR falló')})
            with open(ocr_result['output_path'], 'r', encoding='utf-8', errors='ignore') as tf:
                text = tf.read()
            # Buscar patrón de DNI (simplificado: 8 dígitos y una letra)
            match = re.search(r'\b(\d{8}[A-Za-z])\b', text)
            dni = match.group(1) if match else None
            return jsonify({'success': True, 'dni': dni, 'text': text})
        else:
            return jsonify({'success': False, 'error': f'Acción desconocida: {action}'})
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(temp_path)
        except Exception:
            pass


# ============= ADMINISTRACIÓN =============

@app.route('/admin/users')
@login_required
def admin_users():
    """Gestión de usuarios (solo admin)"""
    if current_user.username != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    conn = sql.connect(USERS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, theme, color_scheme FROM users')
    users = cursor.fetchall()
    conn.close()

    return render_template('admin_users.html', users=users)


@app.route('/admin/config')
@login_required
def admin_config():
    """Configuración del sistema y proveedores de IA"""
    if current_user.username != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    deps_status = check_dependencies()
    # Leer configuración de proveedores para la plantilla
    ai_config = config_manager.load_config()
    ai_providers = ai_config.get('providers', [])
    active_provider_id = ai_config.get('default_provider')
    return render_template('admin_config.html', deps=deps_status,
                           ai_providers=ai_providers,
                           active_provider_id=active_provider_id)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configuración de usuario (tema, colores)"""
    if request.method == 'POST':
        theme = request.form.get('theme', 'auto')
        color_scheme = request.form.get('color_scheme', 'green')

        # Guardar selección en la base de datos
        conn = sql.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET theme=?, color_scheme=? WHERE id=?',
                      (theme, color_scheme, current_user.id))
        conn.commit()
        conn.close()

        # Actualizar el objeto ``current_user`` en memoria para que los cambios
        # surtan efecto inmediatamente en la sesión actual.  De lo contrario,
        # el usuario tendría que volver a iniciar sesión para ver el nuevo
        # tema o esquema de color aplicado en las plantillas.
        current_user.theme = theme
        current_user.color_scheme = color_scheme

        flash('Configuración actualizada', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html')


# ============= ENDPOINTS DE PROVEEDORES DE IA =============

@app.route('/admin/api/providers/add', methods=['POST'])
@login_required
def api_add_provider():
    """Crear un nuevo proveedor de IA.

    Este endpoint acepta un cuerpo JSON con los campos ``name``,
    ``type``, ``api_key``, ``base_url`` y ``model``.  Un identificador
    único se genera automáticamente.  Tras añadir el proveedor, el
    archivo de configuración se actualiza y, si no existe un
    proveedor activo, el recién creado se establece como por defecto.
    """
    if current_user.username != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    provider_type = (data.get('type') or '').strip()
    api_key = (data.get('api_key') or '').strip()
    base_url = (data.get('base_url') or '').strip()
    model = (data.get('model') or '').strip()
    if not name or not provider_type:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    provider_id = str(uuid4())
    provider = {
        'id': provider_id,
        'name': name,
        'type': provider_type.lower(),
        'api_key': api_key,
        'base_url': base_url,
        'model': model,
    }
    config_manager.add_provider(provider)
    return jsonify({'status': 'ok', 'provider_id': provider_id})


@app.route('/admin/api/providers/activate/<provider_id>', methods=['POST'])
@login_required
def api_activate_provider(provider_id: str):
    """Establecer un proveedor como activo.

    Actualiza el campo ``default_provider`` en el archivo de
    configuración.  Si el proveedor no existe, se responde con un
    error 404.
    """
    if current_user.username != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403
    if not config_manager.get_provider_by_id(provider_id):
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    config_manager.activate_provider(provider_id)
    return jsonify({'status': 'ok'})


@app.route('/admin/api/providers/delete/<provider_id>', methods=['DELETE'])
@login_required
def api_delete_provider(provider_id: str):
    """Eliminar un proveedor de IA.

    Remueve el proveedor de la lista.  Si el proveedor eliminado era
    el activo y quedan más proveedores, el primero de la lista se
    convierte en el nuevo activo; de lo contrario, no habrá proveedor
    activo.
    """
    if current_user.username != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403
    if not config_manager.get_provider_by_id(provider_id):
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    config_manager.remove_provider(provider_id)
    return jsonify({'status': 'ok'})


@app.route('/admin/api/providers/test/<provider_id>', methods=['GET'])
@login_required
def api_test_provider(provider_id: str):
    """Probar la conectividad con un proveedor.

    Crea una instancia del proveedor solicitado y ejecuta su método
    ``test_connection``.  Devuelve ``{"status": "ok"}`` si la
    conexión es satisfactoria; de lo contrario devuelve un objeto
    ``{"status": "error", "message": "..."}``.
    """
    if current_user.username != 'admin':
        return jsonify({'status': 'error', 'message': 'Acceso denegado'}), 403
    provider_data = config_manager.get_provider_by_id(provider_id)
    if not provider_data:
        return jsonify({'status': 'error', 'message': 'Proveedor no encontrado'}), 404
    # Construir proveedor concreto usando la misma lógica que en get_active_provider
    ptype = provider_data.get('type')
    api_key = provider_data.get('api_key')
    base_url = provider_data.get('base_url') or ''
    name = provider_data.get('name', provider_id)
    model = provider_data.get('model')
    if ptype != 'ollama':
        # Currently only the Ollama provider is supported.  Future
        # implementations may add additional provider classes.  If an
        # unsupported type is encountered, return an error immediately.
        return jsonify({'status': 'error', 'message': f'Proveedor de tipo "{ptype}" no soportado'}), 400
    # Lazily import the provider class to avoid circular imports
    from ia_providers import OllamaCloudProvider
    provider_instance = OllamaCloudProvider(
        provider_id=provider_id,
        name=name,
        api_key=api_key or '',
        base_url=base_url or 'https://ollama.com',
        model=model or 'gpt-oss:20b-cloud',
    )
    try:
        ok = provider_instance.test_connection()
        if ok:
            return jsonify({'status': 'ok'})
        # Provide a descriptive message if the connection test fails
        return jsonify({'status': 'error', 'message': 'La conexión falló'})
    except Exception as exc:  # noqa: BLE001
        return jsonify({'status': 'error', 'message': str(exc)})


# ============= FUNCIONES AUXILIARES =============

def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def log_process(input_path, output_path, mode='single', action='ocr'):
    """Registrar proceso en base de datos"""
    try:
        # Use the configured path for the logs database
        conn = sql.connect(LOGS_DB_PATH)
        cursor = conn.cursor()

        original_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
        new_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        cursor.execute('''INSERT INTO logs
                         (input_path, output_path, original_size, new_size, timestamp, mode, action, user_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (input_path, output_path, original_size, new_size,
                       datetime.now().isoformat(), mode, action,
                       current_user.id if current_user.is_authenticated else None))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f'Error registrando log: {str(e)}')
        return False


# ============= DESCARGA DE ARCHIVOS PROCESADOS =============

@app.route('/downloads/<path:filename>')
@login_required
def download_processed(filename: str):
    """Descargar un archivo PDF procesado.

    Esta ruta sirve los archivos almacenados en la carpeta de
    subidas ``UPLOAD_FOLDER`` bajo el nombre proporcionado.  Al
    utilizar ``send_from_directory`` en lugar de ``send_file``,
    evitamos problemas de permisos en algunos navegadores y
    ofrecemos una URL sencilla que el usuario puede pulsar para
    iniciar la descarga.

    Parameters
    ----------
    filename: str
        Nombre del archivo a descargar.  Debe existir en
        ``UPLOAD_FOLDER``; de lo contrario se devuelve un error 404.

    Returns
    -------
    flask.Response
        Respuesta con el archivo para descarga o un error si no existe.
    """
    directory = app.config['UPLOAD_FOLDER']
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except FileNotFoundError:
        flash('Archivo no encontrado', 'error')
        return redirect(url_for('upload'))


# ============= INICIALIZACIÓN =============

if __name__ == '__main__':
    init_app()
    port = int(os.getenv('PORT', 5000))
    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true',
            host='0.0.0.0',
            port=port)