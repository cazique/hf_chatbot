# ./ocr_utils.py
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
from datetime import datetime
import config

def rotar_imagen(image):
    """Detecta la orientación del texto y rota la imagen para corregirla."""
    try:
        osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
        rotation = osd.get('rotate', 0)
        if rotation > 0:
            rotated = image.rotate(-rotation, expand=True, fillcolor="white")
            return rotated
    except Exception as e:
        print(f"Error en la detección de orientación: {e}")
    return image

def recortar_a4(image_np):
    """Encuentra el contorno más grande (asumiendo que es el documento) y lo recorta."""
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            # Transformación de perspectiva
            rect = np.zeros((4, 2), dtype="float32")
            s = screenCnt.sum(axis=2)
            rect[0] = screenCnt[np.argmin(s)]
            rect[2] = screenCnt[np.argmax(s)]
            diff = np.diff(screenCnt, axis=2)
            rect[1] = screenCnt[np.argmin(diff)]
            rect[3] = screenCnt[np.argmax(diff)]

            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))

            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))

            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype="float32")

            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image_np, M, (maxWidth, maxHeight))
            return warped

    return image_np # Devuelve original si no encuentra contorno de 4 puntos

def procesar_documento(image_bytes: bytes, user_session_id: str):
    """
    Procesa una imagen de documento: la recorta, la rota y extrae el texto.
    Guarda la imagen procesada y devuelve la información.
    """
    # Convertir bytes a imagen de OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 1. Recortar perspectiva
    recortada_np = recortar_a4(img_np)

    # Convertir a PIL para rotación y OCR
    imagen_pil = Image.fromarray(cv2.cvtColor(recortada_np, cv2.COLOR_BGR2RGB))

    # 2. Corregir orientación
    imagen_rotada = rotar_imagen(imagen_pil)

    # 3. Extraer texto con Tesseract
    texto_ocr = pytesseract.image_to_string(imagen_rotada, lang='spa')

    # 4. Guardar la imagen procesada
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"doc_{user_session_id}_{timestamp}.png"
    ruta_guardada = os.path.join(config.DOCS_DIR, nombre_archivo)
    imagen_rotada.save(ruta_guardada, "PNG")

    return {
        "nombre_archivo": nombre_archivo,
        "ruta_guardada": ruta_guardada,
        "texto_ocr": texto_ocr.strip()
    }
