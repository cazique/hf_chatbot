# ./app.py

import chainlit as cl
import os
import json
from datetime import datetime

# Langchain & Ollama
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Módulos locales
import auth
import db
import config
import ocr_utils
import pdf_utils
import legal

# Inicializar la base de datos al arrancar
db.init_db()

# --- Plantillas de Prompts ---
PROMPT_TEMPLATE = """
Eres 'JustiBot', un asistente legal experto en la generación de contratos para la inmobiliaria 'Hogar Feliz'.
Tu tarea es ayudar a los agentes a crear borradores de contratos de intermediación inmobiliaria.
Debes ser preciso, formal y utilizar un lenguaje legal apropiado para España.

**Historial de Conversación:**
{chat_history}

**Documentos Analizados (OCR):**
{documentos_ocr}

**Instrucción del Agente:**
{input}

**Instrucciones Adicionales:**
1. Si la información es insuficiente, haz preguntas claras y concisas para obtener los detalles que faltan.
2. No inventes datos. Si no tienes un dato, pregunta por él.
3. El flujo principal es conversacional. Responde a las preguntas del agente.
4. Solo cuando el agente diga explícitamente "generar contrato", iniciarás el flujo de preguntas estructuradas para el contrato.
5. Responde siempre en español.

**Respuesta del Asistente:**
"""
prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


# --- LÓGICA DE LOGIN ---

async def local_login_flow():
    """Maneja el login local con usuario/contraseña de config.py"""
    user_resp = await cl.AskUserMessage(content="Usuario:", timeout=120).send()
    if not user_resp: return False
    username = user_resp["content"].strip().lower()

    if username not in config.LOCAL_USERS:
        await cl.Message(content="Usuario local incorrecto.").send()
        return False

    pass_resp = await cl.AskPassword(content="Contraseña:", timeout=120).send()
    if not pass_resp: return False
    password = pass_resp

    user_hash = config.LOCAL_USERS[username]
    if not config.bcrypt_context.verify(password, user_hash):
        await cl.Message(content="Contraseña incorrecta.").send()
        return False

    user = db.get_or_create_user(username, f"{username}@local.hogarfamiliar")
    if not user:
         await cl.Message(content="Error de base de datos al iniciar sesión.").send()
         return False

    cl.user_session.set("user", user)
    return True

async def check_login():
    """Verifica el login, primero por JWT (SSO) y luego por fallback local."""
    if await auth.check_jwt_login():
        return True
    return await local_login_flow()


# --- LÓGICA DE NEGOCIO PRINCIPAL ---

def get_session_chat_history(user_id, session_id):
    """Recupera el historial de chat de la sesión desde la BD y lo formatea."""
    history_tuples = db.get_chat_history(user_id, session_id)
    return "\n".join([f"{'Agente' if is_user else 'Asistente'}: {msg}" for msg, is_user in history_tuples])

def get_ocr_text_from_session():
    """Recupera y formatea el texto OCR de los documentos subidos en la sesión."""
    documentos = cl.user_session.get("documentos_subidos", [])
    if not documentos:
        return "No se han analizado documentos todavía."

    ocr_texts = [f"--- Documento: {doc['nombre_archivo']} ---\n{doc['texto_ocr']}" for doc in documentos]
    return "\n-------------------------------------\n\n".join(ocr_texts)


async def generar_contrato_flow():
    """Guía al usuario para recopilar la información del contrato."""
    s = cl.user_session
    user_data = s.get("user")
    username = user_data['username']
    user_id = user_data['id']

    datos_contrato = {}
    preguntas = {
        "LUGAR": "Lugar de firma del contrato:",
        "LISTA_VENDEDORES": "Nombre completo y DNI de los vendedores (separados por comas si hay varios):",
        "DIRECCION_INMUEBLE": "Dirección completa del inmueble:",
        "REF_CATASTRAL": "Referencia catastral:",
        "TITULO_PROPIEDAD": "Título de propiedad (ej: escritura de compraventa):",
        "CARGAS": "Cargas y gravámenes (o 'Ninguna'):",
        "PRECIO_INMUEBLE": "Precio de venta en cifras (ej: 250000):",
        "PRECIO_INMUEBLE_LETRAS": "Precio de venta en letras (ej: doscientos cincuenta mil):",
        "HONORARIOS": "Porcentaje de honorarios (ej: 3):",
        "EXCLUSIVIDAD": "Tipo de exclusividad (ej: 'exclusiva' o 'no exclusiva'):",
        "MESES_EXCLUSIVIDAD": "Meses de duración del contrato (ej: 6):",
        "LUGAR_JURISDICCION": "Lugar de jurisdicción (ciudad):"
    }

    for clave, pregunta in preguntas.items():
        res = await cl.AskUserMessage(content=pregunta, timeout=300).send()
        if not res:
            await cl.Message("Proceso cancelado por inactividad.").send()
            return
        datos_contrato[clave] = res['content']

    await cl.Message("Gracias. Generando el borrador del contrato PDF...").send()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"borrador_contrato_{username}_{timestamp}.pdf"
    output_path = os.path.join(config.PDF_DIR, output_filename)

    pdf_path = pdf_utils.generar_contrato_pdf_con_plantilla(datos_contrato, output_path, username)

    if pdf_path:
        db.guardar_contrato(user_id, json.dumps(datos_contrato), pdf_path)
        pdf_element = cl.File(name=os.path.basename(pdf_path), path=pdf_path, display="inline")
        await cl.Message(content="Aquí tienes el borrador del contrato.", elements=[pdf_element]).send()
    else:
        await cl.Message("Error al generar el PDF del contrato.").send()


async def generar_pdf_documentos():
    """Une los documentos subidos y procesados en un único PDF."""
    s = cl.user_session
    user_data = s.get("user")
    username = user_data['username']
    documentos = s.get("documentos_subidos", [])

    if not documentos:
        await cl.Message("No hay documentos subidos para procesar.").send()
        return

    await cl.Message("Uniendo los documentos procesados en un único PDF...").send()

    rutas_imagenes = [doc['ruta_guardada'] for doc in documentos]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"documentos_{username}_{timestamp}.pdf"
    output_path = os.path.join(config.PDF_DIR, output_filename)

    pdf_path = pdf_utils.unir_imagenes_a_pdf(rutas_imagenes, output_path)

    if pdf_path:
        pdf_element = cl.File(name=os.path.basename(pdf_path), path=pdf_path, display="inline")
        await cl.Message(content="Aquí tienes el PDF con todos los documentos subidos.", elements=[pdf_element]).send()
    else:
        await cl.Message("Error al generar el PDF de los documentos.").send()


# --- HANDLERS DE CHAINLIT ---

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("headers", cl.context.session.http_request.headers)
    if not await check_login():
        return

    user = cl.user_session.get("user")

    providers = config.PROVIDERS
    if len(providers) == 1:
        cl.user_session.set("selected_ia", providers[0])
    else:
        actions = [cl.Action(name=p['name'], value=p['name'], label=p['name']) for p in providers]
        try:
            res = await cl.AskActionMessage(content="Selecciona el modelo de IA:", actions=actions, timeout=120).send()
            selected_provider = next((p for p in providers if p['name'] == res.get("value")), providers[0])
            cl.user_session.set("selected_ia", selected_provider)
        except TimeoutError:
            cl.user_session.set("selected_ia", providers[0])
            await cl.Message(content="Selección por defecto aplicada.").send()

    selected_ia_name = cl.user_session.get("selected_ia")['name']
    await cl.Message(content=f"Bienvenido, {user['username']}.\n\nUsando **{selected_ia_name}**. ¿En qué puedo ayudarte?", author="JustiBot").send()

    await cl.Message(content=legal.get_footer_js(), disable_feedback=True, author="System").send()

    if user.get('is_admin'):
        cl.user_session.set("is_admin", True)
        await cl.Message(content="**Modo Administrador activado.**\nPuedes usar `/admin_users`.", author="System").send()


@cl.on_message
async def on_message(msg: cl.Message):
    user = cl.user_session.get("user")
    if not user:
        await cl.Message(content="Error de sesión. Recarga la página.").send()
        return

    user_id, session_id = user['id'], cl.user_session.id
    text_content = msg.content.strip().lower()

    db.save_chat_message(user_id, session_id, msg.content, is_user_message=True)

    if text_content == "/admin_users" and cl.user_session.get("is_admin"):
        users = db.get_all_users()
        table_rows = [f"| {u['id']} | {u['username']} | {u['email']} | {u['is_admin']} |" for u in users]
        markdown_table = "\n".join(["| ID | Username | Email | Is Admin |", "|----|----------|-------|----------|"] + table_rows)
        await cl.Message(content=f"**Usuarios Registrados:**\n\n{markdown_table}").send()
        return

    if msg.elements:
        docs = cl.user_session.get("documentos_subidos", [])
        for el in msg.elements:
            if "image" in el.mime:
                await cl.Message(content=f"Procesando `{el.name}`...").send()
                try:
                    info = await cl.make_async(ocr_utils.procesar_documento)(await cl.make_async(el.content), str(user_id))
                    docs.append(info)
                    await cl.Message(content=f"✅ `{info['nombre_archivo']}` procesado.\n**Texto:**\n> {info['texto_ocr'][:200]}...").send()
                except Exception as e:
                    await cl.Message(content=f"Error al procesar `{el.name}`: {e}").send()
        cl.user_session.set("documentos_subidos", docs)
        if not text_content: return

    if "generar contrato" in text_content:
        await generar_contrato_flow()
        return

    if "procesar documentos" in text_content or "ya está" in text_content:
        await generar_pdf_documentos()
        return

    provider = cl.user_session.get("selected_ia")
    llm = Ollama(base_url=provider['url'], model=config.OLLAMA_MODEL, temperature=config.TEMPERATURE)
    chain = prompt | llm | StrOutputParser()

    message_to_llm = cl.Message(content="", author="JustiBot")
    async for chunk in chain.astream({
        "chat_history": get_session_chat_history(user_id, session_id),
        "documentos_ocr": get_ocr_text_from_session(),
        "input": msg.content
    }):
        await message_to_llm.stream_token(chunk)

    await message_to_llm.send()
    db.save_chat_message(user_id, session_id, message_to_llm.content, is_user_message=False)
