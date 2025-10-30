# ocr_utils.py - OCR avanzado
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import re
from datetime import datetime
from config import DOCS_DIR


def rotar_imagen(img):
    # Detectar ángulo
    try:
        osd = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
        angle = int(osd["rotate"])
        if angle != 0:
            img = img.rotate(-angle, expand=True, resample=Image.BICUBIC)
    except:
        pass
    return img


def recortar_a4(img):
    # Convertir a OpenCV
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        cv_img = cv_img[y:y + h, x:x + w]
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


def procesar_dni(imagen_path, es_anverso=True):
    img = Image.open(imagen_path)
    img = rotar_imagen(img)
    img = recortar_a4(img)

    # OCR
    text = pytesseract.image_to_string(img, lang='spa')
    dni = re.search(r'\b(\d{8}[A-Z])\b', text)
    nombre = re.search(r'(?i)nombre\s*[:\-]?\s*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+)', text)
    fecha_cad = re.search(r'(\d{2}[\/\-]\d{2}[\/\-]\d{4})', text)  # aproximado

    dni_str = dni.group(1) if dni else "NO_DNI"
    nombre_str = nombre.group(1).strip() if nombre else "NO_NOMBRE"
    caducidad = fecha_cad.group(1) if fecha_cad else "NO_FECHA"

    # Guardar optimizado
    suffix = "anverso" if es_anverso else "reverso"
    nombre_archivo = f"{dni_str}_{suffix}_{datetime.now():%Y%m%d_%H%M%S}_{caducidad.replace('/', '-')}.jpg"
    ruta_opt = os.path.join(DOCS_DIR, nombre_archivo)
    img.save(ruta_opt, quality=95, optimize=True)

    return {
        "dni": dni_str,
        "nombre": nombre_str,
        "caducidad": caducidad,
        "ruta": ruta_opt,
        "ocr": text
    }