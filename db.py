# ./db.py

import pymysql
import hashlib
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Error al conectar a MariaDB: {e}")
        return None

def hash_password(password):
    """Genera un hash seguro de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_table():
    """Crea la tabla de usuarios si no existe."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(64) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            connection.commit()
        finally:
            connection.close()

def create_chat_history_table():
    """Crea la tabla de historial de chat si no existe."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        session_id VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        is_user_message BOOLEAN NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
            connection.commit()
        finally:
            connection.close()

def get_user_by_username(username):
    """Busca un usuario por su nombre de usuario."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                return cursor.fetchone()
        finally:
            connection.close()
    return None

def get_user_by_id(user_id):
    """Busca un usuario por su ID."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (user_id,))
                return cursor.fetchone()
        finally:
            connection.close()
    return None

def get_all_users():
    """Recupera todos los usuarios de la base de datos."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, email, is_admin FROM users")
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error al obtener todos los usuarios: {e}")
            return []
        finally:
            connection.close()
    return []


def save_chat_message(user_id, session_id, message, is_user_message):
    """Guarda un mensaje de chat en la base de datos."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO chat_history (user_id, session_id, message, is_user_message) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (user_id, session_id, message, is_user_message))
            connection.commit()
        finally:
            connection.close()

def get_chat_history(user_id, session_id):
    """Recupera el historial de chat para una sesión de usuario."""
    connection = get_db_connection()
    history = []
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT message, is_user_message FROM chat_history WHERE user_id = %s AND session_id = %s ORDER BY timestamp ASC"
                cursor.execute(sql, (user_id, session_id))
                result = cursor.fetchall()
                for row in result:
                    history.append((row['message'], row['is_user_message']))
        finally:
            connection.close()
    return history

def initialize_database():
    """Inicializa las tablas de la base de datos."""
    create_user_table()
    create_chat_history_table()
    # Aquí se podría añadir un usuario administrador por defecto si no existe
    # Por ejemplo, checkear si existe 'admin' y si no, crearlo.
