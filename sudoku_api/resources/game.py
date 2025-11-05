from flask_restx import Resource
from flask import request
from sudoku_api.database import PuzzleDB
from sudoku_api.sudoku_game import OptimizedSudokuGameGenerator
from sudoku_api.resources import get_db


class GameResource(Resource):
    def get(self):
        try:
            iterations = request.args.get("iterations", 70, type=int)

            if not 10 <= iterations <= 200:
                return {"error": "Invalid iterations parameter"}, 400

            db = get_db()
            difficulty = request.args.get("difficulty", "MEDIUM", type=str)
            cached_puzzle = db.find_puzzle(difficulty)

            if cached_puzzle:
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
                            "iterations_used": iterations,
                            "empty_cells": len(empty_cells),
                            "cached": True,
                            "hints_coordinates": hints,
                        },
                    },
                }, 200

            if iterations > 80:
                return {"error": "Complex puzzles not yet supported"}, 400

            game = OptimizedSudokuGameGenerator.generate_puzzle(iterations)
            db.save_puzzle(game)

            empty_cells = self._get_empty_cells(game.playable.grid)
            hints = [[r, c] for r, c in empty_cells]

            return {
                "success": True,
                "data": {
                    "playable": {
                        "grid": game.playable.grid,
                        "is_valid": game.playable.is_valid,
                    },
                    "solution": {
                        "grid": game.solution.grid,
                        "is_valid": game.solution.is_valid,
                    },
                    "difficulty": {
                        "level": game.difficult_level.name,
                        "coefficient": round(game.difficult_coefficient, 2),
                    },
                    "metadata": {
                        "iterations_used": iterations,
                        "empty_cells": len(empty_cells),
                        "cached": False,
                        "hints_coordinates": hints,
                    },
                },
            }, 200

        except Exception as e:
            return {"error": "Failed to generate game", "message": str(e)}, 500

    @staticmethod
    def _get_empty_cells(grid):
        return [(i, j) for i in range(9) for j in range(9) if grid[i][j] == 0]
