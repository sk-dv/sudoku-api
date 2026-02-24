import logging
from flask_restx import Resource
from flask import request
from sudoku_api.resources import get_db
from sudoku_api.enums import DifficultyLevel

logger = logging.getLogger(__name__)


class GameResource(Resource):
    @staticmethod
    def _get_difficulty_level(difficulty_input):
        try:
            if difficulty_input is None:
                return DifficultyLevel.get_default()
            else:
                return DifficultyLevel.from_string(difficulty_input)
        except (ValueError, AttributeError):
            return DifficultyLevel.EASY

    def get(self):
        try:
            db = get_db()
            difficulty_input = request.args.get("difficulty", None, type=str)

            difficulty_level = GameResource._get_difficulty_level(difficulty_input)
            cached_puzzle = db.find_puzzle(difficulty_level.db_name)

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
                        "level": difficulty_level.name,
                        "coefficient": round(cached_puzzle["coefficient"], 2),
                    },
                    "metadata": {
                        "empty_cells": len(empty_cells),
                        "cached": True,
                        "hints_coordinates": hints,
                    },
                },
            }, 200

        except Exception:
            logger.exception("Failed to generate game")
            return {"error": "Failed to generate game"}, 500

    @staticmethod
    def _get_empty_cells(grid):
        return [(i, j) for i in range(9) for j in range(9) if grid[i][j] == 0]
