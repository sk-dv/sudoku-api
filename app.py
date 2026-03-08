"""
Sudoku Champions API - Main Application Entry Point
"""

import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from sudoku_api.monitoring import init_sentry
from sudoku_api.config import Config
from sudoku_api.api_models import create_models
from sudoku_api.extensions import limiter
from sudoku_api.middleware import register_hooks
from sudoku_api.routes import register_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

init_sentry()


def create_app():
    app = Flask(__name__)

    for key, value in Config.__dict__.items():
        if not key.startswith("_"):
            app.config[key] = value

    origins = os.environ.get("CORS_ORIGINS", "*").split(",")
    CORS(app, origins=origins)

    limiter.init_app(app)
    register_hooks(app)

    api = Api(
        app,
        version="2.0.0",
        title="Sudoku Champions API",
        description="API para generar, validar y resolver puzzles de Sudoku",
        doc="/api/docs",
        prefix="/api",
    )

    models = create_models(api)
    register_routes(api, models)

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
