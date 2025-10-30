# contrato_bot.py - Versión Intermediación Inmobiliaria (Actualizado 30/10/2025)
import chainlit as cl
from PIL import Image
import pytesseract
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import re
from datetime import datetime
import hashlib
from jinja2 import Template  # Para rellenar plantillas con variables

# Configuración
OUTPUT_DIR = "contratos"
PLANTILLA_PATH = "plantilla_intermediacion.txt"  # Guarda la plantilla arriba como TXT
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Usuarios demo
USERS = {
    "ivan": hashlib.sha256("1234".encode()).hexdigest(),
    "maria": hashlib.sha256("secreto".encode()).hexdigest()
}

# Cargar plantilla
with open(PLANTILLA_PATH, 'r', encoding='utf-8') as f:
    PLANTILLA_TEXTO = f.read()


def generar_intermediacion_pdf(datos, pdf_path):
    # Renderizar plantilla con variables
    template = Template(PLANTILLA_TEXTO)
    texto_renderizado = template.render(datos)

    # Generar PDF (multi-línea para texto largo)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin = 50
    line_height = 12  # Más pequeña para caber todo
    y = height - margin
    lines = texto_renderizado.split('\n')

    for line in lines:
        if y < 50:  # Nueva página si se acaba
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line[:80])  # Línea max 80 chars; ajusta para wrap
        y -= line_height

    c.save()


def extraer_dni_ocr(imagen):
    try:
        text = pytesseract.image_to_string(imagen, lang='spa')
        dni_match = re.search(r'\b(\d{8}[A-Z])\b', text)
        nombre_match = re.search(r'(?i)nombre\s*[:\-]?\s*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+)', text)
        dni = dni_match.group(1) if dni_match else "No detectado"
        nombre = nombre_match.group(1).strip() if nombre_match else "No detectado"
        return {"dni": dni, "nombre": nombre, "raw": text}
    except Exception as e:
        return {"error": str(e)}


async def verificar_login():
    if cl.user_session.get("logged_in"):
        return True
    await cl.Message(content="Inicia sesión para continuar").send()
    user_response = await cl.AskUserMessage(content="Usuario:", timeout=60).send()
    username = user_response["content"].strip().lower()
    if username not in USERS:
        await cl.Message(content="Usuario incorrecto.").send()
        return False
    pass_response = await cl.AskUserMessage(content="Contraseña:", password=True, timeout=60).send()
    password = pass_response["content"]
    pass_hash = hashlib.sha256(password.encode()).hexdigest()
    if pass_hash != USERS[username]:
        await cl.Message(content="Contraseña incorrecta.").send()
        return False
    cl.user_session.set("logged_in", True)
    cl.user_session.set("username", username)
    await cl.Message(content="Login correcto").send()
    return True


@cl.on_chat_start
async def start():
    cl.set_page_config(
        title="Hogar Familiar | Contrato Intermediación",
        description="Genera contratos de intermediación con validación legal",
        favicon="public/logo.png",
    )
    if not await verificar_login():
        return
    username = cl.user_session.get("username", "Usuario").capitalize()
    js_saludo = f"""
    <script>
    document.addEventListener("DOMContentLoaded", () => {{
        const hora = new Date().getHours();
        let saludo;
        if (hora >= 5 && hora < 12) saludo = "¡Buenos días";
        else if (hora < 20) saludo = "¡Buenas tardes";
        else saludo = "¡Buenas noches";
        const texto = `${{saludo}}, <strong>${{username}}</strong>! ¿En qué puedo ayudarte hoy?`;
        const mensaje = document.querySelector('.cl-bot-message:last-child .message-content');
        if (mensaje) mensaje.innerHTML = texto;
    }});
    </script>
    <div>Cargando saludo...</div>
    """
    await cl.Message(content=js_saludo, disable_human_feedback=True).send()
    await cl.Message(
        content="Vamos a crear un **contrato de intermediación**. Sube DNIs de propietarios y responde preguntas.").send()


@cl.on_message
async def main(message: cl.Message):
    if not cl.user_session.get("logged_in"):
        await cl.Message(content="Sesión expirada. Inicia sesión.").send()
        await start()
        return

    session = cl.user_session  # Shorthand
    if message.elements:  # Upload DNI
        await cl.Message(content="Procesando DNI(s)...").send()
        for elem in message.elements:
            if elem.type == "image":
                img = Image.open(elem.path)
                datos = extraer_dni_ocr(img)
                if "error" not in datos:
                    propietarios = session.get("propietarios", [])
                    propietarios.append(datos)
                    session.set("propietarios", propietarios)
        await cl.Message(
            content=f"Propietarios detectados: {len(session.get('propietarios', []))}. Continúa con preguntas.").send()
    else:
        text = message.content.lower()
        if "generar" in text or "contrato" in text:
            # Recopilar campos faltantes si no completos
            if len(session.get("propietarios", [])) == 0:
                num_prop = await cl.AskUserMessage(content="¿Cuántos propietarios? (1-4)").send()
                session.set("num_prop", int(num_prop["content"]))
                for i in range(int(num_prop["content"])):
                    await cl.Message(content=f"Propietario {i + 1}: Sube DNI.").send()
                return  # Espera uploads
            # Preguntas guiadas (simplificado; expande con más AskUserMessage)
            lugar = (await cl.AskUserMessage(content="Lugar de firma (ej. Madrid):")).get("content", "Madrid")
            direccion_inmueble = (await cl.AskUserMessage(content="Dirección del inmueble:")).get("content", "")
            precio = (await cl.AskUserMessage(content="Precio de venta (€):")).get("content", "0")
            honorarios = (await cl.AskUserMessage(content="Honorarios (€, IVA excl.):")).get("content", "7000")
            exclusividad = (await cl.AskUserMessage(content="Exclusividad? (sí/no):")).get("content", "sí")
            duracion = (await cl.AskUserMessage(content="Duración (meses):")).get("content", "3")
            jurisdiccion = (await cl.AskUserMessage(content="Jurisdicción (ej. Alcalá de Henares):")).get("content",
                                                                                                          "Alcalá de Henares")

            # Construir lista vendedores (con OCR)
            lista_vendedores = []
            for prop in session.get("propietarios", []):
                lista_vendedores.append(f"D. {prop['nombre']} con DNI {prop['dni']}, domicilio en {direccion_inmueble}")
            lista_vendedores_str = " y ".join(lista_vendedores)
            es_son = "es" if len(lista_vendedores) == 1 else "son"
            firmas = "\n".join([f"[Firma {i + 1}]" for i in range(len(lista_vendedores))])

            # Datos para plantilla
            datos = {
                "FECHA": datetime.now().strftime("%d/%m/%Y"),
                "LUGAR": lugar,
                "LISTA_VENDEDORES": lista_vendedores_str,
                "ES_SON": es_son,
                "DIRECCION_INMUEBLE": direccion_inmueble,
                "MUNICIPIO": "Madrid",  # De PDF; haz dinámico
                "PROVINCIA": "Madrid",
                "PRECIO_VENTA": precio,
                "HONORARIOS": honorarios,
                "EXCLUSIVIDAD": exclusividad,
                "DURACION_MES": duracion,
                "URL_DATOS_INMO": "https://hogarfamiliar.es/privacidad",  # Tu sitio
                "JURISDICCION": jurisdiccion,
                "REPRESENTANTE_INMO": "Ivan Muñoz León",
                "FIRMAS_VENDEDORES": firmas,
                "USUARIO_GENERADOR": session.get("username", "Usuario"),
                "FECHA_GENERACION": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            # Generar PDF
            username = session.get("username", "usuario")
            pdf_name = f"intermediacion_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
            generar_intermediacion_pdf(datos, pdf_path)

            await cl.Message(content="¡Contrato generado! Descárgalo y revísalo legalmente.",
                             elements=[cl.File(name=pdf_name, path=pdf_path)]).send()
            session.clear()  # Reset para nuevo
        else:
            await cl.Message(content="Escribe 'generar contrato' para empezar el flujo.").send()