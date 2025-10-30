import chainlit as cl
import ollama
import os
from datetime import datetime
import json
import logging

# Importaciones de módulos locales
import config
import db
import auth
import legal
import ocr_utils
import pdf_utils

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializar la base de datos al arrancar la aplicación
db.init_db()

CONTRACT_QUESTIONS = {
    "Nombre Cliente": "¿Cuál es el nombre completo del cliente?",
    "DNI Cliente": "¿Cuál es el DNI del cliente?",
    "Dirección Cliente": "¿Cuál es la dirección completa del cliente?",
    "Nombre Agente": "¿Cuál es tu nombre completo como agente?",
    "DNI Agente": "¿Cuál es tu DNI?",
    "Ciudad": "¿En qué ciudad se firma el contrato?",
    "Dirección Inmueble": "¿Cuál es la dirección completa del inmueble?",
    "Precio Inmueble": "¿Cuál es el precio de venta/alquiler en Euros?",
    "Porcentaje Honorarios": "¿Cuál es el porcentaje de honorarios para la agencia?",
    "Duración Contrato": "¿Cuál es la duración del contrato en meses?"
}

@cl.on_chat_start
async def on_chat_start():
    await cl.set_page_config(
        "Chatbot Legal Inmobiliario",
        favicon="public/favicon.ico",
        hide_cot=True,
        stylesheets=["public/style.css"]
    )

    # Simulación de login para desarrollo
    user = db.get_or_create_user(username="usuario_dev", email="dev@example.com")
    if not user:
        await cl.Message(content="Error: No se pudo crear el usuario de desarrollo.").send()
        return
    cl.user_session.set("user", user)

    history = db.load_chat_history(user["id"])
    cl.user_session.set("history", history)
    cl.user_session.set("documentos_subidos", [])
    cl.user_session.set("contract_flow_data", None)

    await cl.Message(
        content=f"¡Buenos días, {user['username']}! Soy tu asistente legal. Para generar un contrato, escribe **'generar contrato'**. También puedo ayudarte a procesar documentos.",
        author="Asistente"
    ).send()
    await legal.get_footer_js().send()

@cl.on_message
async def on_message(message: cl.Message):
    user = cl.user_session.get("user")
    history = cl.user_session.get("history")

    # Si estamos en el flujo de creación de contrato
    contract_flow_data = cl.user_session.get("contract_flow_data")
    if contract_flow_data is not None:
        await handle_contract_flow(message, contract_flow_data)
        return

    # Guardar mensaje y añadirlo al historial
    db.save_chat_message(user["id"], 'user', message.content)
    history.append({"role": "user", "content": message.content})

    # Iniciar flujo de contrato
    if "generar contrato" in message.content.lower():
        await start_contract_flow()
        return

    # Procesamiento de documentos
    if message.elements:
        for element in message.elements:
            if "image" in element.mime:
                docs = cl.user_session.get("documentos_subidos")
                docs.append(element)
                cl.user_session.set("documentos_subidos", docs)
                await cl.Message(
                    content=f"Recibido: `{element.name}`. Cuando termines, di **'procesar documentos'**.",
                    author="Asistente"
                ).send()
                return

    if "procesar documentos" in message.content.lower():
        await generar_pdf_documentos(user)
        return

    # Respuesta de la IA
    await get_ia_response(history)

async def start_contract_flow():
    """Inicia el flujo de preguntas para generar el contrato."""
    contract_flow_data = {"answers": {}, "questions": list(CONTRACT_QUESTIONS.keys())}
    cl.user_session.set("contract_flow_data", contract_flow_data)
    first_question_key = contract_flow_data["questions"][0]
    await cl.Message(content=CONTRACT_QUESTIONS[first_question_key], author="Asistente").send()

async def handle_contract_flow(message: cl.Message, flow_data: dict):
    """Maneja las respuestas del usuario durante la creación del contrato."""
    user = cl.user_session.get("user")
    current_question_key = flow_data["questions"][len(flow_data["answers"])]
    flow_data["answers"][current_question_key] = message.content

    # Si quedan más preguntas
    if len(flow_data["answers"]) < len(flow_data["questions"]):
        next_question_key = flow_data["questions"][len(flow_data["answers"])]
        await cl.Message(content=CONTRACT_QUESTIONS[next_question_key], author="Asistente").send()
    else:
        # Hemos terminado, generar el PDF
        await generate_contract_pdf(flow_data["answers"])
        cl.user_session.set("contract_flow_data", None) # Salir del flujo

async def generate_contract_pdf(answers: dict):
    """Genera y envía el PDF del contrato."""
    user = cl.user_session.get("user")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"Contrato_{answers['Nombre Cliente']}_{timestamp}.pdf"
    output_path = os.path.join(config.UPLOADS_DIR, pdf_filename)

    # Añadir fecha actual
    answers['día'] = datetime.now().strftime('%d')
    answers['mes'] = datetime.now().strftime('%B')
    answers['año'] = datetime.now().strftime('%Y')

    pdf_path = pdf_utils.generar_contrato_pdf(
        datos=answers,
        plantilla="plantilla_intermediacion.txt",
        output_path=output_path
    )

    if pdf_path:
        elements = [cl.File(name=pdf_filename, path=pdf_path, display="inline")]
        await cl.Message(content="He generado el contrato con los datos que me has proporcionado.", elements=elements, author="Asistente").send()

        # Guardar en la base de datos
        db.guardar_contrato(user["id"], datetime.now().date(), pdf_path, json.dumps(answers))
    else:
        await cl.Message(content="Lo siento, ha ocurrido un error al generar el PDF del contrato.", author="Sistema").send()


async def generar_pdf_documentos(user):
    """Procesa los documentos subidos (imágenes) y los une en un PDF."""
    documentos = cl.user_session.get("documentos_subidos")
    if not documentos:
        await cl.Message(content="No has subido ningún documento para procesar.", author="Asistente").send()
        return

    msg = cl.Message(content="Procesando documentos...", author="Sistema", disable_feedback=True)
    await msg.send()

    image_paths = []
    for doc in documentos:
        temp_path = os.path.join(config.UPLOADS_DIR, f"{user['username']}_{doc.name}")
        with open(doc.path, "rb") as f_in, open(temp_path, "wb") as f_out:
            f_out.write(f_in.read())
        image_paths.append(temp_path)

    if image_paths:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"Documentacion_{user['username']}_{timestamp}.pdf"
        pdf_path = os.path.join(config.UPLOADS_DIR, pdf_filename)

        pdf_utils.unir_imagenes_a_pdf(image_paths, pdf_path)

        await msg.update(content="He generado un PDF con tus documentos.")
        elements = [cl.File(name=pdf_filename, path=pdf_path, display="inline")]
        await cl.Message(content="Aquí tienes el PDF.", elements=elements, author="Asistente").send()

        cl.user_session.set("documentos_subidos", [])
        for path in image_paths:
            os.remove(path)
    else:
        await msg.update(content="No se encontraron imágenes válidas.")

async def get_ia_response(history):
    """Obtiene y muestra una respuesta del modelo de IA."""
    msg = cl.Message(content="", author="Asistente")
    stream_content = ""

    try:
        response = await ollama.AsyncClient(host=config.OLLAMA_BASE_URL).chat(
            model='llama3', messages=history, stream=True
        )
        async for part in response:
            if token := part["message"]["content"]:
                await msg.stream_token(token)
                stream_content += token
        await msg.send()

        if stream_content:
            user_id = cl.user_session.get("user")["id"]
            db.save_chat_message(user_id, 'assistant', stream_content)
            history.append({"role": "assistant", "content": stream_content})

    except Exception as e:
        logging.error(f"Error al contactar con Ollama: {e}")
        await cl.Message(content="Lo siento, estoy teniendo problemas para conectar con mi cerebro.", author="Sistema").send()
