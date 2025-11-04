FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-spa \
    poppler-utils ghostscript \
    && rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 5000
VOLUME /app/uploads

CMD ["python", "app.py"]