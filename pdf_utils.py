from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from PIL import Image
import os
import logging
import json
from jinja2 import Environment, FileSystemLoader

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generar_contrato_pdf(datos: dict, plantilla: str, output_path: str):
    """
    Genera un contrato en PDF a partir de una plantilla de texto y un diccionario de datos.

    Args:
        datos (dict): Diccionario con los datos para rellenar la plantilla.
        plantilla (str): La ruta al archivo de plantilla (.txt).
        output_path (str): Ruta donde se guardará el PDF resultante.
    """
    try:
        # Configurar Jinja2 para leer la plantilla
        env = Environment(loader=FileSystemLoader(os.path.dirname(plantilla)))
        template = env.get_template(os.path.basename(plantilla))

        # Renderizar la plantilla con los datos
        contenido = template.render(datos)

        # Crear el PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        text = c.beginText(1.5 * cm, height - 2 * cm)
        text.setFont("Helvetica", 10)
        text.setLeading(14)

        for line in contenido.split('\\n'):
            text.textLine(line)

        c.drawText(text)
        c.save()
        logger.info(f"Contrato PDF generado exitosamente en: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error al generar el contrato PDF: {e}")
        return None

def unir_imagenes_a_pdf(image_paths: list, output_pdf_path: str):
    """
    Toma una lista de rutas de imágenes y las une en un único archivo PDF.
    Cada imagen se colocará en una página separada, ajustada al tamaño de la página.

    Args:
        image_paths (list): Lista de rutas a los archivos de imagen.
        output_pdf_path (str): Ruta donde se guardará el PDF resultante.
    """
    if not image_paths:
        logger.warning("No se proporcionaron imágenes para unir en el PDF.")
        return

    try:
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        width, height = letter

        for i, image_path in enumerate(image_paths):
            try:
                with Image.open(image_path) as img:
                    img_width, img_height = img.size

                    aspect = img_height / float(img_width)

                    new_width = width * 0.8 # Dejar márgenes
                    new_height = new_width * aspect

                    if new_height > height * 0.9:
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

    except Exception as e:
        logger.error(f"Error al crear el PDF de imágenes: {e}")
        raise
