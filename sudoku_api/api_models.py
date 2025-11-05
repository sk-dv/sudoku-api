"""Modelos de API para documentación de Swagger"""

from flask_restx import fields


def create_models(api):
    """Crea todos los modelos de la API
    
    Args:
        api: Instancia de la API Flask-RESTX
        
    Returns:
        dict: Diccionario con todos los modelos creados
    """
    
    grid_model = api.model(
        "Grid",
        {
            "grid": fields.List(
                fields.List(fields.Integer, description="Row of 9 integers (0-9)"),
                description="9x9 Sudoku grid (0 = empty cell)",
            )
        },
    )

    playable_model = api.model(
        "Playable", 
        {
            "grid": fields.Raw, 
            "is_valid": fields.Boolean
        }
    )

    solution_model = api.model(
        "Solution", 
        {
            "grid": fields.Raw, 
            "is_valid": fields.Boolean
        }
    )

    difficulty_model = api.model(
        "Difficulty", 
        {
            "level": fields.String, 
            "coefficient": fields.Float
        }
    )

    metadata_model = api.model(
        "Metadata",
        {
            "iterations_used": fields.Integer,
            "empty_cells": fields.Integer,
            "cached": fields.Boolean,
            "is_daily": fields.Boolean(required=False),
            "date_assigned": fields.String(required=False),
        },
    )

    game_response_model = api.model(
        "GameResponse",
        {
            "success": fields.Boolean,
            "data": fields.Nested(
                api.model(
                    "GameData",
                    {
                        "playable": fields.Nested(playable_model),
                        "solution": fields.Nested(solution_model),
                        "difficulty": fields.Nested(difficulty_model),
                        "metadata": fields.Nested(metadata_model),
                    },
                )
            ),
        },
    )

    return {
        "grid": grid_model,
        "playable": playable_model,
        "solution": solution_model,
        "difficulty": difficulty_model,
        "metadata": metadata_model,
        "game_response": game_response_model,
    }
