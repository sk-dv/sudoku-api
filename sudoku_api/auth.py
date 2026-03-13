import os
import base64
import json
import logging
from functools import wraps
from flask import request, g

logger = logging.getLogger(__name__)

_API_KEY = os.environ.get("API_KEY")
_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app

    creds_b64 = os.environ.get("FIREBASE_CREDENTIALS")
    if not creds_b64:
        raise EnvironmentError("FIREBASE_CREDENTIALS no está configurada")

    creds_json = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
    cert = credentials.Certificate(creds_json)
    _firebase_app = firebase_admin.initialize_app(cert)
    return _firebase_app


def require_api_key(f):
    """Sin-op si API_KEY no está definida en el entorno."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if _API_KEY and request.headers.get("X-API-Key") != _API_KEY:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated


def require_firebase_auth(f):
    """Verifica el Firebase ID token del header Authorization: Bearer <token>.
    Inyecta g.firebase_uid y g.firebase_email si el token es válido.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid Authorization header"}, 401

        id_token = auth_header.split("Bearer ", 1)[1].strip()
        if not id_token:
            return {"error": "Missing token"}, 401

        try:
            from firebase_admin import auth
            _get_firebase_app()
            decoded = auth.verify_id_token(id_token)
            g.firebase_uid = decoded["uid"]
            g.firebase_email = decoded.get("email", "")
            g.firebase_name = decoded.get("name", "")
        except Exception as e:
            logger.warning("Firebase token verification failed: %s", e)
            return {"error": "Invalid or expired token"}, 401

        return f(*args, **kwargs)
    return decorated
