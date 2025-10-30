# pdf_utils.py
import os
import logging
import json
import textwrap
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LÓGICA DE PLANTILLA (de 02b8ffea) ---
try:
    env = Environment(loader=FileSystemLoader(os.path.dirname(config.PLANTILLA_PATH)))
    TEMPLATE = env.get_template(os.path.basename(config.PLANTILLA_PATH))
except Exception as e:
    logger.error(f"Error cargando plantilla Jinja2: {e}")
    TEMPLATE = None

def generar_contrato_pdf_con_plantilla(datos: dict, output_path: str, usuario: str):
    """Genera un PDF de contrato rellenando la plantilla legal."""
    if not TEMPLATE:
        logger.error("No se puede generar el PDF: Plantilla no cargada.")
        return None

    try:
        # Añadir datos de la inmobiliaria al contexto de la plantilla
        datos_completos = {
            **datos,
            "FECHA": datetime.now().strftime("%d/%m/%Y"),
            "FECHA_GENERACION": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "REPRESENTANTE_INMO": f"D. {config.INMO['representante']}",
            "INMO_CIF": config.INMO['cif'],
            "INMO_DIRECCION": config.INMO.get('direccion', 'Dirección no especificada'),
            "USUARIO_GENERADOR": usuario.capitalize(),
            "URL_DATOS_INMO": config.INMO.get('url', 'https://hogarfamiliar.es/privacidad')
        }
        texto = TEMPLATE.render(datos_completos)

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        margin = 60
        y = height - margin
        line_height = 14

        c.setFont("Helvetica", 10)

        for linea in texto.split('\\n'):
            for wrapped in textwrap.wrap(linea, width=85, replace_whitespace=False):
                if y < 80: # Margen inferior
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - margin
                c.drawString(margin, y, wrapped)
                y -= line_height
            y -= 4 # Espacio extra entre párrafos (líneas en blanco)
        c.save()
        logger.info(f"Contrato PDF generado exitosamente en: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error al generar el contrato PDF: {e}")
        return None

# --- LÓGICA DE UNIR IMÁGENES (de bd84bfd) ---
def unir_imagenes_a_pdf(image_paths: list, output_pdf_path: str):
    """Toma una lista de rutas de imágenes (ya procesadas) y las une en un PDF."""
    if not image_paths:
        logger.warning("No se proporcionaron imágenes para unir en el PDF.")
        return None

    try:
        c = canvas.Canvas(output_pdf_path, pagesize=A4)
        width, height = A4

        for i, image_path in enumerate(image_paths):
            try:
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                    aspect = img_height / float(img_width)

                    new_width = width * 0.9 # Márgenes del 5%
                    new_height = new_width * aspect

                    if new_height > height * 0.9: # Si es más alta que la página
                        new_height = height * 0.9
                        new_width = new_height / aspect

                    x_centered = (width - new_width) / 2
                    y_centered = (height - new_height) / 2

                    c.drawImage(image_path, x_centered, y_centered, width=new_width, height=new_height, preserveAspectRatio=True)

                    if i < len(image_paths) - 1:
                        c.showPage()

            except Exception as e:
                logger.error(f"No se pudo procesar la imagen {image_path}: {e}")
                c.drawString(100, height / 2, f"Error al cargar la imagen: {os.path.basename(image_path)}")
                if i < len(image_paths) - 1:
                    c.showPage()

        c.save()
        logger.info(f"PDF de imágenes generado exitosamente en: {output_pdf_path}")
        return output_pdf_path
    except Exception as e:
        logger.error(f"Error al crear el PDF de imágenes: {e}")
        return None
