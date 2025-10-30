
import db

def add_test_user():
    """Añade un usuario de prueba a la base de datos."""
    connection = db.get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Comprobar si el usuario ya existe
                cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
                if cursor.fetchone():
                    print("El usuario 'testuser' ya existe.")
                    return

                # Si no existe, crearlo
                password_hash = db.hash_password('testpassword')
                sql = "INSERT INTO users (username, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, ('testuser', 'test@example.com', password_hash, False))
            connection.commit()
            print("Usuario 'testuser' creado con éxito.")
        finally:
            connection.close()

if __name__ == "__main__":
    db.initialize_database()
    add_test_user()
