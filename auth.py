import jwt
import logging
import config
import db

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_from_token(token: str):
    """
    Valida un token JWT, y si es válido, obtiene o crea el usuario correspondiente.

    Args:
        token: El token JWT a validar.

    Returns:
        Un diccionario con los datos del usuario si el token es válido, de lo contrario None.
    """
    if not token:
        logger.warning("Se intentó validar un token vacío.")
        return None

    try:
        # Decodificar el token usando la clave pública y el algoritmo de la configuración
        decoded_token = jwt.decode(
            token,
            config.JWT_PUBLIC_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )

        username = decoded_token.get("username")
        email = decoded_token.get("email")

        if not username or not email:
            logger.error(f"Token inválido: faltan 'username' o 'email'. Payload: {decoded_token}")
            return None

        # Con el email y username, obtenemos o creamos el usuario en nuestra DB
        user = db.get_or_create_user(username=username, email=email)

        if not user:
            logger.error(f"No se pudo obtener o crear el usuario: {username} ({email})")
            return None

        logger.info(f"Token validado correctamente para el usuario: {user['username']}")
        return user

    except jwt.ExpiredSignatureError:
        logger.warning("El token ha expirado.")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Error al decodificar el token JWT: {e}")
        return None
    except Exception as e:
        logger.critical(f"Error inesperado durante la validación del token: {e}")
        return None
