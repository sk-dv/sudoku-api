from flask_restx import Resource
from flask import request
from sudoku_api.resources import get_db
from sudoku_api.enums import DifficultLevel


class GameResource(Resource):
    def get(self):
        try:
            db = get_db()
            difficulty_input = request.args.get("difficulty", None, type=str)

            # Validar y parsear el nivel de dificultad
            try:
                if difficulty_input is None:
                    difficulty_level = DifficultLevel.get_default()
                else:
                    difficulty_level = DifficultLevel.from_string(difficulty_input)
            except ValueError as ve:
                return {"error": "Invalid difficulty level", "message": str(ve)}, 400

            cached_puzzle = db.find_puzzle(difficulty_level.name)
            empty_cells = self._get_empty_cells(cached_puzzle["playable_grid"])
            hints = [[r, c] for r, c in empty_cells]

            return {
                "success": True,
                "data": {
                    "playable": {
                        "grid": cached_puzzle["playable_grid"],
                        "is_valid": False,
                    },
                    "solution": {
                        "grid": cached_puzzle["solution_grid"],
                        "is_valid": True,
                    },
                    "difficulty": {
                        "level": cached_puzzle["difficulty"],
                        "coefficient": round(cached_puzzle["coefficient"], 2),
                    },
                    "metadata": {
                        "empty_cells": len(empty_cells),
                        "cached": True,
                        "hints_coordinates": hints,
                    },
                },
            }, 200

        except Exception as e:
            return {"error": "Failed to generate game", "message": str(e)}, 500

    @staticmethod
    def _get_empty_cells(grid):
        return [(i, j) for i in range(9) for j in range(9) if grid[i][j] == 0]
