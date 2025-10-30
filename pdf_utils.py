# ./pdf_utils.py

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from config import PDF_DIR
import time
from PIL import Image as PILImage
import io

def crear_pdf_contrato(username, chat_history, image_paths):
    """
    Crea un documento PDF con el historial del chat y las imágenes de los documentos.

    Args:
        username (str): Nombre del usuario para el título.
        chat_history (str): El historial de la conversación formateado.
        image_paths (list): Lista de rutas a las imágenes procesadas para adjuntar.

    Returns:
        str: La ruta al archivo PDF generado.
    """
    timestamp = int(time.time())
    pdf_path = os.path.join(PDF_DIR, f"borrador_contrato_{username}_{timestamp}.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título
    title = f"Borrador de Contrato - Agente: {username}"
    story.append(Paragraph(title, styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    # Sección de Conversación
    story.append(Paragraph("Historial de la Conversación", styles['h2']))
    # Reemplazar saltos de línea para que se muestren correctamente en el PDF
    formatted_history = chat_history.replace('\n', '<br/>\n')
    story.append(Paragraph(formatted_history, styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))

    # Sección de Documentos Adjuntos
    if image_paths:
        story.append(Paragraph("Documentos Adjuntos (Imágenes Procesadas)", styles['h2']))

        for img_path in image_paths:
            try:
                # Comprobar si el archivo existe
                if not os.path.exists(img_path):
                    print(f"Advertencia: No se encontró la imagen en {img_path}")
                    story.append(Paragraph(f"Error: No se pudo cargar la imagen {os.path.basename(img_path)}", styles['BodyText']))
                    continue

                # Añadir nombre de archivo
                story.append(Paragraph(f"<i>{os.path.basename(img_path)}</i>", styles['Italic']))
                story.append(Spacer(1, 0.1 * inch))

                # Redimensionar la imagen para que quepa en la página
                # Ancho máximo de 6 pulgadas (aproximadamente el ancho del área de texto)
                max_width = 6 * inch
                max_height = 8 * inch # Altura máxima para evitar que ocupe toda la página

                # Usar Pillow para abrir la imagen y obtener sus dimensiones sin cargarla completamente en memoria de reportlab de inmediato
                with PILImage.open(img_path) as p_img:
                    original_width, original_height = p_img.size

                aspect_ratio = original_height / float(original_width)

                display_width = max_width
                display_height = display_width * aspect_ratio

                if display_height > max_height:
                    display_height = max_height
                    display_width = display_height / aspect_ratio

                # Crear el objeto Image de reportlab
                img = Image(img_path, width=display_width, height=display_height)
                story.append(img)
                story.append(Spacer(1, 0.2 * inch))

            except Exception as e:
                print(f"Error al procesar la imagen {img_path} para el PDF: {e}")
                story.append(Paragraph(f"Error al cargar la imagen: {os.path.basename(img_path)}", styles['BodyText']))

    # Construir el PDF
    try:
        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"Error al construir el PDF: {e}")
        return None
