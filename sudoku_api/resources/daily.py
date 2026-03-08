import logging
from datetime import date
from flask_restx import Resource
from flask import request
from sudoku_api.resources import get_db
from sudoku_api.enums import DifficultyLevel

logger = logging.getLogger(__name__)


class DailyPuzzleResource(Resource):
    def get(self):
        try:
            db = get_db()
            today = date.today()
            day_of_year = today.timetuple().tm_yday

            difficulty_input = request.args.get("difficulty", None, type=str)
            difficulty_level = (
                DifficultyLevel.from_string(difficulty_input)
                if difficulty_input
                else DifficultyLevel.get_default()
            )

            puzzle = db.find_daily_puzzle(difficulty_level.name, day_of_year)

            if not puzzle:
                return {"error": "No hay puzzle diario para este nivel"}, 404
            empty_cells = self._get_empty_cells(puzzle["playable_grid"])

            return {
                "success": True,
                "data": {
                    "playable": {
                        "grid": puzzle["playable_grid"],
                        "is_valid": False,
                    },
                    "solution": {
                        "grid": puzzle["solution_grid"],
                        "is_valid": True,
                    },
                    "difficulty": {
                        "level": difficulty_level.name,
                        "coefficient": round(puzzle["coefficient"], 2),
                    },
                    "metadata": {
                        "empty_cells": len(empty_cells),
                        "cached": True,
                        "is_daily": True,
                        "date_assigned": str(today),
                        "hints_coordinates": [[r, c] for r, c in empty_cells],
                    },
                },
            }, 200

        except Exception:
            logger.exception("Failed to get daily puzzle")
            return {"error": "Failed to get daily puzzle"}, 500

    @staticmethod
    def _get_empty_cells(grid):
        return [(i, j) for i in range(9) for j in range(9) if grid[i][j] == 0]