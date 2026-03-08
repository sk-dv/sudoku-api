import os
from functools import wraps
from flask import request

_API_KEY = os.environ.get("API_KEY")


def require_api_key(f):
    """Sin-op si API_KEY no está definida en el entorno."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if _API_KEY and request.headers.get("X-API-Key") != _API_KEY:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated
