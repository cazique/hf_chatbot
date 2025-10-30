# ./auth.py
import chainlit as cl
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import config
import db

async def check_jwt_login():
    """
    Verifica si hay un token JWT en los headers de la sesión, lo valida
    y establece el usuario en la sesión de Chainlit si es válido.
    """
    session = cl.user_session
    headers = session.get("headers")

    if not headers or "Authorization" not in headers:
        return False

    auth_header = headers["Authorization"]
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False

    token = parts[1]

    try:
        if not config.JWT_PUBLIC_KEY:
            return False

        public_key = f"-----BEGIN PUBLIC KEY-----\\n{config.JWT_PUBLIC_KEY}\\n-----END PUBLIC KEY-----"

        payload = jwt.decode(
            token,
            public_key,
            algorithms=[config.ALGORITHM]
        )

        username = payload.get("preferred_username", "sso_user")
        email = payload.get("email", f"{username}@sso.hogarfamiliar")
        is_admin = "admin" in payload.get("realm_access", {}).get("roles", [])

        user = db.get_or_create_user(username, email, is_admin)
        if not user:
            return False

        cl.user_session.set("user", user)
        return True

    except (ExpiredSignatureError, InvalidTokenError) as e:
        print(f"Error de validación JWT: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado en validación JWT: {e}")
        return False
