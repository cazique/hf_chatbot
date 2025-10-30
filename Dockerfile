# Usar una imagen base de Python 3.12 slim
FROM python:3.12-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Instalar dependencias del sistema operativo necesarias para
# Tesseract (motor de OCR), OpenCV (procesamiento de imágenes) y otras librerías.
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    # Limpiar la caché de apt para reducir el tamaño de la imagen
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt requirements.txt

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que Chainlit se ejecuta por defecto
EXPOSE 8000

# Comando para iniciar la aplicación Chainlit
# --host 0.0.0.0 para que sea accesible desde fuera del contenedor
# --port 8000 para que coincida con el puerto expuesto
# -w para habilitar el auto-reload (útil para desarrollo, opcional para producción)
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "-w"]
