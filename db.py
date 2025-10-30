import mysql.connector
from mysql.connector import errorcode
import config
import logging
from datetime import datetime

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establece y devuelve una conexión con la base de datos."""
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASS,
            database=config.DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.error("Error de acceso: verifica usuario y contraseña.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logger.error(f"La base de datos '{config.DB_NAME}' no existe.")
        else:
            logger.error(f"Error al conectar con la base de datos: {err}")
        return None

def init_db():
    """Crea las tablas de la base de datos si no existen."""
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()

    tables = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """,
        "contratos": """
            CREATE TABLE IF NOT EXISTS contratos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                fecha DATE,
                pdf_path VARCHAR(255),
                datos_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """,
        "chat_history": """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                role ENUM('user', 'assistant') NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """
    }

    try:
        for table_name, table_description in tables.items():
            logger.info(f"Creando tabla '{table_name}'...")
            cursor.execute(table_description)
    except mysql.connector.Error as err:
        logger.error(f"Error al crear las tablas: {err}")
    finally:
        cursor.close()
        conn.close()

def get_or_create_user(username, email):
    """
    Busca un usuario por su email. Si no existe, lo crea.
    Devuelve el objeto de usuario (id, username, email, is_admin).
    """
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        # Buscar usuario por email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Si el username ha cambiado, actualizarlo
            if user['username'] != username:
                cursor.execute("UPDATE users SET username = %s WHERE email = %s", (username, email))
                conn.commit()
                user['username'] = username
            return user

        # Si no existe, crearlo
        cursor.execute(
            "INSERT INTO users (username, email, is_admin) VALUES (%s, %s, %s)",
            (username, email, False) # Por defecto, no es admin
        )
        conn.commit()

        # Obtener el usuario recién creado
        cursor.execute("SELECT * FROM users WHERE id = %s", (cursor.lastrowid,))
        new_user = cursor.fetchone()
        return new_user

    except mysql.connector.Error as err:
        logger.error(f"Error en la base de datos (get_or_create_user): {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_chat_message(user_id, role, content):
    """Guarda un mensaje del chat en la base de datos."""
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, role, content)
        )
        conn.commit()
    except mysql.connector.Error as err:
        logger.error(f"Error al guardar mensaje de chat: {err}")
    finally:
        cursor.close()
        conn.close()

def load_chat_history(user_id):
    """Carga el historial de chat de un usuario desde la base de datos."""
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    history = []
    try:
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY timestamp ASC",
            (user_id,)
        )
        for row in cursor.fetchall():
            history.append({"role": row["role"], "content": row["content"]})
        return history
    except mysql.connector.Error as err:
        logger.error(f"Error al cargar historial de chat: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def guardar_contrato(user_id, fecha, pdf_path, datos_json):
    """Guarda los datos de un contrato en la base de datos."""
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO contratos (user_id, fecha, pdf_path, datos_json) VALUES (%s, %s, %s, %s)",
            (user_id, fecha, pdf_path, datos_json)
        )
        conn.commit()
        logger.info(f"Contrato guardado para el usuario {user_id} en {pdf_path}")
    except mysql.connector.Error as err:
        logger.error(f"Error al guardar contrato: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    logger.info("Inicializando la base de datos...")
    init_db()
    logger.info("Base de datos lista.")
