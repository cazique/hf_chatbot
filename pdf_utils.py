# pdf_utils.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from jinja2 import Template
from config import PLANTILLA_PATH, INMO
from datetime import datetime
import textwrap

with open(PLANTILLA_PATH, 'r', encoding='utf-8') as f:
    TEMPLATE = Template(f.read())

def generar_pdf(datos, path, usuario):
    texto = TEMPLATE.render({
        **datos,
        "FECHA": datetime.now().strftime("%d/%m/%Y"),
        "FECHA_GENERACION": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "REPRESENTANTE_INMO": f"D. {INMO['representante']}",
        "USUARIO_GENERADOR": usuario.capitalize(),
        **INMO
    })

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    margin = 60
    y = height - margin
    line_height = 14

    for linea in texto.split('\n'):
        if y < 80:
            c.showPage()
            y = height - margin
        for wrapped in textwrap.wrap(linea, width=85):
            c.drawString(margin, y, wrapped)
            y -= line_height
        y -= 4
    c.save()