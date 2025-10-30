# ./app.py

import chainlit as cl
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import auth
import db
import config
import ocr_utils
import pdf_utils
from legal import get_legal_context_for_contract, get_initial_legal_html

# Inicializar la base de datos al arrancar
db.initialize_database()

# --- Plantillas de Prompts ---
PROMPT_TEMPLATE = """
Eres 'JustiBot', un asistente legal experto en la generación de contratos para la inmobiliaria 'Hogar Feliz'.
Tu tarea es ayudar a los agentes a crear borradores de contratos de alquiler basados en la información proporcionada.
Debes ser preciso, formal y utilizar un lenguaje legal apropiado para España.

**Contexto Legal Relevante:**
{legal_context}

**Historial de Conversación:**
{chat_history}

**Documentos Analizados (OCR):**
{documentos_ocr}

**Instrucción del Agente:**
{input}

**Instrucciones Adicionales:**
1. Si la información es insuficiente, haz preguntas claras y concisas para obtener los detalles que faltan.
2. No inventes datos. Si no tienes un dato, pregunta por él.
3. Al final, cuando el agente lo indique con una frase como "genera el contrato" o "ya está todo",
   proporciona un resumen final y confirma que el documento PDF ha sido generado.
4. Responde siempre en español.

**Respuesta del Asistente:**
"""

prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

# --- Funciones de Lógica de la Aplicación ---

def get_session_chat_history(user_id, session_id):
    """Recupera el historial de chat de la sesión desde la BD y lo formatea."""
    history_tuples = db.get_chat_history(user_id, session_id)
    history_str = ""
    for msg, is_user in history_tuples:
        role = "Agente" if is_user else "Asistente"
        history_str += f"{role}: {msg}\n"
    return history_str

def get_ocr_text_from_session():
    """Recupera y formatea el texto OCR de los documentos subidos en la sesión."""
    documentos = cl.user_session.get("documentos_subidos", [])
    if not documentos:
        return "No se han analizado documentos todavía."

    ocr_completo = ""
    for doc in documentos:
        ocr_completo += f"--- Documento: {doc['nombre_archivo']} ---\n"
        ocr_completo += doc['texto_ocr']
        ocr_completo += "\n-------------------------------------\n\n"
    return ocr_completo


async def generar_pdf_documentos():
    """Genera un PDF con la información y documentos de la sesión."""
    user = cl.user_session.get("user")
    chat_history = get_session_chat_history(user['id'], cl.user_session.id)
    documentos = cl.user_session.get("documentos_subidos", [])

    # Extraer las rutas de las imágenes procesadas
    rutas_imagenes = [doc['ruta_guardada'] for doc in documentos]

    pdf_path = pdf_utils.crear_pdf_contrato(
        user['username'],
        chat_history,
        rutas_imagenes
    )
    return pdf_path

# --- Handlers de Chainlit ---

@cl.on_chat_start
async def on_chat_start():
    # 1. Autenticación JWT
    if not await auth.check_jwt_login():
        return  # Detiene la ejecución si el login falla

    user = cl.user_session.get("user")

    # 2. Selección de proveedor de IA
    providers = config.PROVIDERS
    if not providers:
        await cl.Message(content="Error: No hay proveedores de IA configurados. Contacte al administrador.").send()
        return

    actions = [cl.Action(name=p['name'], value=p['name'], label=p['name']) for p in providers]

    try:
        res = await cl.AskActionMessage(
            content="Por favor, selecciona el modelo de IA para esta sesión.",
            actions=actions,
            timeout=60 # Tiempo de espera para la selección
        ).send()

        if res:
            selected_provider_name = res.get("value")
            selected_provider = next((p for p in providers if p['name'] == selected_provider_name), None)

            if selected_provider:
                cl.user_session.set("selected_ia", selected_provider)
                await cl.Message(content=f"Has seleccionado **{selected_provider['name']}**. ¡Comencemos!").send()
            else:
                await cl.Message(content="Error: Selección inválida. Usando proveedor por defecto.").send()
                cl.user_session.set("selected_ia", providers[0])
    except TimeoutError:
        await cl.Message(content="No has seleccionado un proveedor. Usando el predeterminado.").send()
        cl.user_session.set("selected_ia", providers[0])


    # 3. Mensaje de bienvenida y panel de administrador
    await cl.Message(
        content=f"Bienvenido de nuevo, {user['username']} a **{config.APP_NAME}**.",
        author="JustiBot"
    ).send()

    if user.get('is_admin'):
        cl.user_session.set("is_admin", True)
        await cl.Message(
            content="**Modo Administrador activado.**\nPuedes usar comandos especiales como `/admin_users`.",
            author="System"
        ).send()

    # Mostrar contexto legal inicial
    await cl.Message(content=get_initial_legal_html(), author="Contexto Legal", disable_feedback=True).send()


@cl.on_message
async def on_message(msg: cl.Message):
    user = cl.user_session.get("user")
    user_id = user['id']
    session_id = cl.user_session.id

    # Guardar mensaje del usuario en la BD
    db.save_chat_message(user_id, session_id, msg.content, is_user_message=True)

    # --- Manejo de Comandos de Administrador ---
    if msg.content.strip() == "/admin_users" and cl.user_session.get("is_admin"):
        users = db.get_all_users()
        if not users:
            await cl.Message(content="No se encontraron usuarios.").send()
            return

        table_header = "| ID | Username | Email | Is Admin |"
        table_divider = "|----|----------|-------|----------|"
        table_rows = [f"| {u['id']} | {u['username']} | {u['email']} | {u['is_admin']} |" for u in users]

        markdown_table = "\n".join([table_header, table_divider] + table_rows)
        await cl.Message(content=f"**Lista de Usuarios Registrados:**\n\n{markdown_table}").send()
        return

    # --- Manejo de Subida de Archivos ---
    if msg.elements:
        documentos_subidos = cl.user_session.get("documentos_subidos", [])
        for element in msg.elements:
            if "image" in element.mime:
                try:
                    await cl.Message(content=f"Procesando imagen: `{element.name}`...").send()
                    bytes_imagen = await cl.make_async(element.content)

                    # Llamada a la función de OCR avanzada
                    info_doc = await cl.make_async(ocr_utils.procesar_documento)(
                        image_bytes=bytes_imagen,
                        user_session_id=str(user_id)
                    )

                    documentos_subidos.append(info_doc)
                    cl.user_session.set("documentos_subidos", documentos_subidos)

                    await cl.Message(
                        content=f"✅ Documento `{info_doc['nombre_archivo']}` procesado y añadido a la sesión.\n"
                                f"**Texto extraído:**\n> {info_doc['texto_ocr'][:200]}..."
                    ).send()

                except Exception as e:
                    await cl.Message(content=f"Error al procesar el documento `{element.name}`: {e}").send()
        # Si hay texto junto con la imagen, no lo procesamos con el LLM todavía,
        # solo confirmamos la subida. El usuario puede luego hacer una pregunta sobre los docs.
        # Si solo se suben imágenes sin texto, retornamos para evitar llamar al LLM con un input vacío.
        if not msg.content:
            return


    # --- Lógica para generar el PDF ---
    if "genera el contrato" in msg.content.lower() or "ya está" in msg.content.lower():
        generating_msg = cl.Message(content="Generando el borrador del contrato en PDF...", author="JustiBot")
        await generating_msg.send()

        pdf_path = await generar_pdf_documentos()

        if pdf_path:
            pdf_element = cl.File(
                name=os.path.basename(pdf_path),
                path=pdf_path,
                display="inline",
                content=open(pdf_path, "rb").read()
            )
            await cl.Message(
                content="Aquí tienes el borrador del contrato. Por favor, revísalo detenidamente.",
                elements=[pdf_element],
                author="JustiBot"
            ).send()
        else:
            await cl.Message(content="Lo siento, ha ocurrido un error al generar el PDF.", author="JustiBot").send()
        return


    # --- Lógica de LLM ---
    provider = cl.user_session.get("selected_ia")
    if not provider:
        await cl.Message(content="Error: No se ha seleccionado un proveedor de IA. Por favor, reinicia el chat.").send()
        return

    llm = Ollama(
        base_url=provider['url'],
        model=config.OLLAMA_MODEL,
        temperature=config.TEMPERATURE,
        # Se pueden añadir headers si la API requiere autenticación, por ejemplo:
        # headers={"Authorization": f"Bearer {provider['key']}"}
    )

    # Preparar el contexto para el prompt
    chat_history = get_session_chat_history(user_id, session_id)
    documentos_ocr = get_ocr_text_from_session()
    legal_context = get_legal_context_for_contract()

    chain = prompt | llm | StrOutputParser()

    message_to_llm = cl.Message(content="", author="JustiBot")
    async for chunk in chain.astream({
        "legal_context": legal_context,
        "chat_history": chat_history,
        "documentos_ocr": documentos_ocr,
        "input": msg.content
    }):
        await message_to_llm.stream_token(chunk)

    await message_to_llm.send()
    # Guardar respuesta del LLM en la BD
    db.save_chat_message(user_id, session_id, message_to_llm.content, is_user_message=False)
