import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import logging
import os
from datetime import datetime

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rotar_imagen(image_path: str):
    """
    Detecta la orientación de una imagen y la rota para que el texto esté vertical.

    Args:
        image_path: Ruta a la imagen.

    Returns:
        La imagen rotada como un objeto de OpenCV.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"No se pudo cargar la imagen desde: {image_path}")
            return None

        # Usar pytesseract para detectar la orientación y el script (OSD)
        osd = pytesseract.image_to_osd(img, output_type=Output.DICT)

        angle = osd.get('rotate', 0)
        logger.info(f"Ángulo de rotación detectado: {angle} grados para {os.path.basename(image_path)}")

        if angle != 0:
            # Rotar la imagen para corregir la orientación
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, -angle, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated

        return img

    except Exception as e:
        logger.error(f"Error al rotar la imagen {image_path}: {e}")
        return cv2.imread(image_path) # Devolver la original en caso de error

def recortar_a4(image: np.ndarray):
    """
    Intenta detectar el contorno de un documento A4 en una imagen y lo recorta.

    Args:
        image: La imagen como un objeto de OpenCV.

    Returns:
        La imagen recortada y con corrección de perspectiva.
    """
    try:
        # Convertir a escala de grises y aplicar desenfoque
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detección de bordes
        edged = cv2.Canny(blurred, 75, 200)

        # Encontrar los contornos
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        # Buscar un contorno con 4 puntos (un rectángulo)
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                screenCnt = approx

                # Aplicar transformación de perspectiva
                rect = np.zeros((4, 2), dtype="float32")
                s = screenCnt.sum(axis=2)
                rect[0] = screenCnt[np.argmin(s)]
                rect[2] = screenCnt[np.argmax(s)]

                diff = np.diff(screenCnt, axis=2)
                rect[1] = screenCnt[np.argmin(diff)]
                rect[3] = screenCnt[np.argmax(diff)]

                (tl, tr, br, bl) = rect

                # Calcular el ancho y alto del nuevo A4
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
                warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
                logger.info("Recorte A4 y corrección de perspectiva aplicados.")
                return warped

        logger.warning("No se encontró un contorno de 4 puntos. Devolviendo imagen original.")
        return image
    except Exception as e:
        logger.error(f"Error durante el recorte A4: {e}")
        return image

def procesar_dni(image_path: str, lado: str, uploads_dir: str):
    """
    Procesa una imagen de DNI: la rota, la recorta y genera un nombre de archivo estandarizado.

    Args:
        image_path: Ruta a la imagen original.
        lado: 'anverso' o 'reverso'.
        uploads_dir: Directorio donde guardar la imagen procesada.

    Returns:
        La ruta a la imagen procesada o None si hay error.
    """
    try:
        # 1. Rotar la imagen
        imagen_rotada = rotar_imagen(image_path)
        if imagen_rotada is None:
            return None

        # 2. Recortar (podría ser una función específica para DNI si es necesario)
        # Por ahora, usamos el recorte genérico A4, que podría no ser ideal para DNI.
        imagen_recortada = recortar_a4(imagen_rotada)

        # 3. Extraer fecha de caducidad para el nombre del archivo (si es anverso)
        fecha_caducidad = "_fecha_desconocida"
        if lado == "anverso":
            try:
                # Intentar leer la fecha (esto es muy propenso a errores)
                texto = pytesseract.image_to_string(imagen_recortada, lang='spa')
                # (Lógica para encontrar una fecha con formato XX.XX.XXXX)
                # ...
                # Si se encuentra, fecha_caducidad = "YYYYMMDD"
                pass # Implementación pendiente
            except Exception:
                logger.warning("No se pudo extraer la fecha de caducidad del DNI.")

        # 4. Generar el nuevo nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        nuevo_nombre = f"DNI_{lado}{fecha_caducidad}_{timestamp}.jpg"
        nueva_ruta = os.path.join(uploads_dir, nuevo_nombre)

        # 5. Guardar la imagen procesada
        cv2.imwrite(nueva_ruta, imagen_recortada)
        logger.info(f"DNI procesado y guardado en: {nueva_ruta}")

        return nueva_ruta

    except Exception as e:
        logger.error(f"Error al procesar el DNI {image_path}: {e}")
        return None

if __name__ == '__main__':
    # Ejemplo de uso (requiere una imagen de prueba)
    # test_image_path = "ruta/a/tu/imagen_dni.jpg"
    # uploads_folder = "uploads"
    # if not os.path.exists(uploads_folder):
    #     os.makedirs(uploads_folder)
    #
    # if os.path.exists(test_image_path):
    #    procesar_dni(test_image_path, "anverso", uploads_folder)
    # else:
    #    logger.warning("El archivo de imagen de prueba no existe.")
    pass
