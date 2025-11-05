from flask_restx import Resource
from flask import request
from datetime import date
from sudoku_api.resources import get_db


class DailyPuzzleResource(Resource):
    def get(self):
        try:
            difficulty = request.args.get("difficulty", "MEDIUM", type=str)
            today = str(date.today())

            db = get_db()
            puzzle = db.find_daily_puzzle(difficulty, today)

            if not puzzle:
                puzzle = db.assign_daily_puzzle(difficulty, today)

            if not puzzle:
                return {
                    "error": "No puzzles available",
                    "message": f"No unassigned puzzles found for difficulty {difficulty}",
                }, 404

            empty_cells = self._get_empty_cells(puzzle["playable_grid"])
            hints = [[r, c] for r, c in empty_cells]

            return {
                "success": True,
                "data": {
                    "date": today,
                    "playable": {
                        "grid": puzzle["playable_grid"],
                        "is_valid": False,
                    },
                    "solution": {
                        "grid": puzzle["solution_grid"],
                        "is_valid": True,
                    },
                    "difficulty": {
                        "level": puzzle["difficulty"],
                        "coefficient": round(puzzle["coefficient"], 2),
                    },
                    "metadata": {
                        "empty_cells": len(empty_cells),
                        "is_daily": True,
                        "date_assigned": today,
                        "hints_coordinates": hints,
                    },
                },
            }, 200

        except Exception as e:
            return {"error": "Failed to get daily puzzle", "message": str(e)}, 500

    @staticmethod
    def _get_empty_cells(grid):
        return [(i, j) for i in range(9) for j in range(9) if grid[i][j] == 0]
