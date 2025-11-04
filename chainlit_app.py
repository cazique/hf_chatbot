"""Aplicación Chainlit para procesar PDFs con OCR y almacenarlos.

Esta aplicación utiliza la biblioteca Chainlit para proporcionar una
interfaz de chat sencilla.  Cuando el usuario adjunta un PDF, el
archivo se guarda temporalmente en la carpeta de subidas de la
aplicación Flask, se ejecuta OCR mediante ``perform_ocr`` y se
almacena el resultado optimizado en la misma carpeta.  El bot
devuelve un mensaje informando de la ruta del archivo procesado.

Para ejecutar este chatbot, instala las dependencias y ejecuta

    chainlit run chainlit_app.py

en el directorio del proyecto.
"""

from __future__ import annotations

import os
import uuid
from typing import Optional

import chainlit as cl
import requests

# Instead of calling OCR functions directly (which require system
# dependencies like Tesseract), this chatbot delegates processing to
# the existing Flask backend.  The backend exposes a REST API
# ``/api/chatbot/upload`` that accepts a file and returns the path
# to the processed PDF.  Set BACKEND_URL via environment variable
# when running in Docker so that requests go to the correct
# service (e.g. "http://immodoc-web:5000").

BACKEND_URL = os.getenv("BACKEND_URL", "http://immodoc-web:5000")

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")


@cl.on_chat_start
async def on_start() -> None:
    """Evento que se ejecuta al iniciar la conversación."""
    await cl.Message(
        content=(
            "Hola 👋. Envía un archivo PDF y lo procesaré con OCR. "
            "Recibirás un enlace al PDF procesado."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Gestionar mensajes entrantes en la conversación."""
    # Si el usuario envía adjuntos, procesarlos mediante la API del backend
    if message.files:
        for uploaded_file in message.files:
            try:
                # Descargar el archivo desde la interfaz de Chainlit
                file_bytes = await uploaded_file.download()
                # Preparar multipart/form-data para la API de Flask
                files = {
                    "file": (uploaded_file.name, file_bytes, uploaded_file.mime or "application/pdf")
                }
                data = {"intent": "ocr"}
                # Enviar a la ruta de chatbot del backend que aplica OCR y optimiza
                resp = requests.post(
                    f"{BACKEND_URL}/api/chatbot/upload", files=files, data=data, timeout=300
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("success"):
                        processed_path = result.get("output_file")
                        # Construir enlace absoluto para descarga (suponemos que el host
                        # immodoc-web está expuesto en el puerto 5000 a través de nginx o
                        # directamente).  Ajusta el dominio según tu despliegue.
                        filename = os.path.basename(processed_path)
                        link = f"/downloads/{filename}"
                        await cl.Message(
                            content=f"✅ Archivo procesado correctamente. Descarga: {link}"
                        ).send()
                    else:
                        await cl.Message(
                            content=f"❌ Error procesando {uploaded_file.name}: {result.get('error', 'desconocido')}"
                        ).send()
                else:
                    await cl.Message(
                        content=f"❌ La API devolvió un error ({resp.status_code}) al procesar {uploaded_file.name}"
                    ).send()
            except Exception as exc:  # noqa: BLE001
                await cl.Message(
                    content=f"❌ Se produjo un error al procesar {uploaded_file.name}: {exc}"
                ).send()
    else:
        # Si no hay adjuntos, enviar un recordatorio al usuario
        await cl.Message(
            content=(
                "Por favor adjunta un archivo PDF o imagen para procesar. "
                "Actualmente, este chatbot solo procesa archivos adjuntos."
            )
        ).send()