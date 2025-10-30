# ./ocr_utils.py

import cv2
import numpy as np
import pytesseract
import config
import os
import time
from PIL import Image

def rotar_imagen(image: np.ndarray) -> np.ndarray:
    """
    Detecta y corrige la orientación de una imagen usando Tesseract OSD.
    Args:
        image: Una imagen en formato NumPy array (leída con OpenCV).
    Returns:
        La imagen rotada en formato NumPy array.
    """
    try:
        # Usar Tesseract para detectar la orientación (OSD - Orientation and Script Detection)
        osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
        angulo = osd.get('rotate', 0)

        # Rotar la imagen para corregir la orientación
        if angulo != 0:
            (h, w) = image.shape[:2]
            centro = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(centro, -angulo, 1.0)
            # Ajustar el tamaño de la imagen para que quepa todo el contenido rotado
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            nuevo_w = int((h * sin) + (w * cos))
            nuevo_h = int((h * cos) + (w * sin))
            M[0, 2] += (nuevo_w / 2) - centro[0]
            M[1, 2] += (nuevo_h / 2) - centro[1]
            imagen_rotada = cv2.warpAffine(image, M, (nuevo_w, nuevo_h), borderValue=(255, 255, 255))
            return imagen_rotada
        return image
    except Exception as e:
        print(f"Error durante la rotación de la imagen: {e}")
        return image # Devuelve la imagen original en caso de error

def recortar_a4(image: np.ndarray) -> np.ndarray:
    """
    Detecta el contorno más grande (asumido como una hoja A4 o DNI)
    y aplica una transformación de perspectiva para obtener una vista cenital.
    Args:
        image: Imagen en formato NumPy array (rotada).
    Returns:
        Imagen recortada y transformada, o la original si no se encuentra un contorno adecuado.
    """
    try:
        # Convertir a escala de grises
        gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Aplicar un desenfoque para reducir el ruido
        gris = cv2.GaussianBlur(gris, (5, 5), 0)
        # Detección de bordes con Canny
        bordes = cv2.Canny(gris, 75, 200)

        # Encontrar contornos
        contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # Ordenar contornos por área de mayor a menor
        contornos = sorted(contornos, key=cv2.contourArea, reverse=True)[:5]

        # Iterar sobre los contornos para encontrar el que parece un documento
        for c in contornos:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # Si el contorno aproximado tiene 4 puntos, asumimos que es nuestro documento
            if len(approx) == 4:
                screenCnt = approx
                break
        else:
            # Si no se encuentra un contorno de 4 puntos, devolver la imagen original
            print("Advertencia: No se encontró un contorno de 4 puntos. Se devuelve la imagen original.")
            return image

        # Aplicar la transformación de perspectiva
        pts = screenCnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        # El orden de los puntos en rect es: top-left, top-right, bottom-right, bottom-left
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        (tl, tr, br, bl) = rect

        # Calcular el ancho de la nueva imagen
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # Calcular la altura de la nueva imagen
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Construir el conjunto de puntos de destino para obtener la vista "aérea"
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # Calcular la matriz de transformación de perspectiva y aplicarla
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped
    except Exception as e:
        print(f"Error durante el recorte de la imagen: {e}")
        return image # Devuelve la imagen original en caso de error

def procesar_documento(image_bytes: bytes, user_session_id: str) -> dict:
    """
    Orquesta el pipeline completo de procesamiento de un documento:
    rotación, recorte, OCR, y guardado.
    Args:
        image_bytes: Los bytes de la imagen subida.
        user_session_id: El ID de la sesión del usuario para nombrar el archivo.
    Returns:
        Un diccionario con la ruta de la imagen guardada, el texto OCR y el nombre del archivo.
    """
    # 1. Cargar la imagen desde bytes a un formato de OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Rotar la imagen para corregir la orientación
    img_rotada = rotar_imagen(img_cv)

    # 3. Recortar la imagen para obtener una vista de "escáner"
    img_procesada = recortar_a4(img_rotada)

    # 4. Extraer texto usando Tesseract OCR de la imagen final
    # Convertir de OpenCV (BGR) a PIL (RGB) que es lo que espera Tesseract
    img_pil = Image.fromarray(cv2.cvtColor(img_procesada, cv2.COLOR_BGR2RGB))
    texto_ocr = pytesseract.image_to_string(img_pil, lang='spa') # 'spa' para español

    # 5. Generar un nombre de archivo único y guardarla
    timestamp = int(time.time())
    nombre_archivo = f"doc_{user_session_id}_{timestamp}.jpg"
    ruta_guardada = os.path.join(config.DOCS_DIR, nombre_archivo)

    # Guardar la imagen procesada (la recortada y rotada)
    cv2.imwrite(ruta_guardada, img_procesada)

    return {
        'ruta_guardada': ruta_guardada,
        'texto_ocr': texto_ocr,
        'nombre_archivo': nombre_archivo
    }
