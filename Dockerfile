# Usa una imagen base ligera de Python 3.12
FROM python:3.12-slim

# Instala Tesseract OCR, el paquete de idioma español y las dependencias de OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requisitos e instálalo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Expone el puerto que usa Chainlit
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
