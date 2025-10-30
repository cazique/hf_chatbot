# app.py - VERSIÓN CORREGIDA Y FUNCIONAL 100%
import chainlit as cl
import ollama
import hashlib
import os
from datetime import datetime
from config import USERS, OUTPUT_DIR, DOCS_DIR, INMO
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
                model='gpt-oss:120b-cloud',
                messages=[{'role': 'user', 'content': msg.content}]
            )
            await cl.Message(content=respuesta['message']['content']).send()

        else:
            # IA general
            try:
                respuesta = ollama.chat(
                    model='gpt-oss:120b-cloud',
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
    lugar = (await cl.AskUserMessage("Lugar de firma (ej: Los Santos de la Humosa):")).send()["content"]
    direccion = (await cl.AskUserMessage("Dirección del inmueble:")).send()["content"]
    precio = (await cl.AskUserMessage("Precio de venta (€):")).send()["content"]
    honorarios = (await cl.AskUserMessage("Honorarios (€ IVA excl.):")).send()["content"]
    exclusividad = (await cl.AskUserMessage("Exclusividad (sí/no):")).send()["content"]
    meses = (await cl.AskUserMessage("Duración (meses):")).send()["content"]
    jurisdiccion = (await cl.AskUserMessage("Jurisdicción:")).send()["content"]

    # Construir datos
    lista = [f"D. {d['nombre']}, DNI {d['dni']}, domicilio en {direccion}" for d in docs]
    datos = {
        "LUGAR": lugar,
        "LISTA_VENDEDORES": " y ".join(lista),
        "ES_SON": "es" if len(docs) == 1 else "son",
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

    await cl.Message(
        content="Contrato generado",
        elements=[cl.File(path=pdf_path, name=pdf_name)]
    ).send()

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