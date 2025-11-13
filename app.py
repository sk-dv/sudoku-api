"""
Sudoku Champions API - Main Application Entry Point

Aplicación Flask para generar, validar y resolver puzzles de Sudoku
con diferentes niveles de dificultad.
"""

from flask import Flask
from flask_cors import CORS
from flask_restx import Api
import os

from sudoku_api.config import Config
from sudoku_api.api_models import create_models
from sudoku_api.routes import register_routes


def create_app():
    """Factory para crear y configurar la aplicación Flask"""
    
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Aplicar configuración
    for key, value in Config.__dict__.items():
        if not key.startswith('_'):
            app.config[key] = value
    
    # Habilitar CORS
    CORS(app)

    # Inicializar API Swagger
    api = Api(
        app,
        version="2.0.0",
        title="Sudoku Champions API",
        description="API para generar, validar y resolver puzzles de Sudoku con diferentes niveles de dificultad",
        doc="/api/docs",
        prefix="/api",
    )

    # Crear modelos de API
    models = create_models(api)

    # Registrar rutas
    register_routes(api, models)

    return app


# Crear la aplicación
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"Starting Sudoku API on port {port}")
    print(f"Debug mode: {debug}")

    app.run(host="0.0.0.0", port=port, debug=debug)
