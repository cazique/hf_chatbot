# db.py - SQLite
import sqlite3
import os
from config import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "hogar_familiar.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY,
            usuario TEXT,
            fecha TEXT,
            pdf_path TEXT,
            datos_json TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY,
            contrato_id INTEGER,
            tipo TEXT,
            nombre_archivo TEXT,
            ruta TEXT,
            ocr_text TEXT,
            fecha_subida TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_contrato(usuario, pdf_path, datos):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO contratos (usuario, fecha, pdf_path, datos_json) VALUES (?, ?, ?, ?)",
              (usuario, datetime.now().isoformat(), pdf_path, str(datos)))
    contrato_id = c.lastrowid
    conn.commit()
    conn.close()
    return contrato_id

def guardar_documento(contrato_id, tipo, nombre, ruta, ocr_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO documentos (contrato_id, tipo, nombre_archivo, ruta, ocr_text, fecha_subida) VALUES (?, ?, ?, ?, ?, ?)",
              (contrato_id, tipo, nombre, ruta, ocr_text, datetime.now().isoformat()))
    conn.commit()
    conn.close()