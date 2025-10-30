# ./auth.py

import chainlit as cl
from passlib.context import CryptContext
import db
import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica una contraseña plana contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def check_jwt_login():
    """
    Gestiona el flujo de login. Pide un token, lo valida, y si no es válido,
    pide credenciales de usuario y contraseña para generar uno nuevo.
    """
    # Intentar obtener el token de la sesión del usuario
    token = cl.user_session.get("auth_token")

    if token:
        try:
            # Decodificar el token para validar la firma y la expiración
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            user = db.get_user_by_id(user_id)
            if user:
                cl.user_session.set("user", user)
                # Opcional: Refrescar el token si está cerca de expirar
                return True
            else:
                # El usuario del token ya no existe
                cl.user_session.set("auth_token", None)
        except jwt.ExpiredSignatureError:
            await cl.Message(content="Tu sesión ha expirado. Por favor, inicia sesión de nuevo.").send()
            cl.user_session.set("auth_token", None)
        except jwt.InvalidTokenError:
            await cl.Message(content="Token inválido. Por favor, inicia sesión de nuevo.").send()
            cl.user_session.set("auth_token", None)

    # Si no hay token o el token es inválido, pedir login
    return await ask_login()

async def ask_login():
    """Pide al usuario su nombre de usuario y contraseña."""
    res = await cl.AskUserMessage(
        content="¡Bienvenido a Hogar Feliz Chatbot! Por favor, inicia sesión para continuar.",
        timeout=300
    ).send()

    if res:
        username = res['output']

        res_pass = await cl.AskUserMessage(
            content=f"Hola, {username}. Por favor, introduce tu contraseña.",
            timeout=300,
            # 'password' en metadata oculta la entrada
            metadata={'type': 'password'}
        ).send()

        if res_pass:
            password = res_pass['output']

            # Autenticar al usuario
            user = db.get_user_by_username(username)
            if user and verify_password(password, user['password_hash']):
                # Generar un nuevo token
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": str(user['id'])}, expires_delta=access_token_expires
                )

                # Guardar token y datos de usuario en la sesión
                cl.user_session.set("auth_token", access_token)

                # Guardamos una versión segura de los datos del usuario, sin el hash de la pass
                user_info = {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "is_admin": user["is_admin"]
                }
                cl.user_session.set("user", user_info)

                await cl.Message(content="¡Inicio de sesión exitoso!").send()
                return True
            else:
                await cl.Message(content="Nombre de usuario o contraseña incorrectos.").send()
                return False

    # Si el usuario no introduce nada o cierra el prompt
    await cl.Message(content="Proceso de inicio de sesión cancelado.").send()
    return False
