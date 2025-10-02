from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields

import os

from sudoku_api.database import PuzzleDB
from sudoku_api.sudoku_game import OptimizedSudokuGameGenerator
from sudoku_api.validator import Validator

puzzle_db = PuzzleDB()

app = Flask(__name__)
CORS(app)

# Configuración
app.config["JSON_SORT_KEYS"] = False
app.config["RESTX_MASK_SWAGGER"] = False

# Inicializar Swagger
api = Api(
    app,
    version="2.0.0",
    title="Sudoku Champions API",
    description="API para generar, validar y resolver puzzles de Sudoku con diferentes niveles de dificultad",
    doc="/api/docs",
)

# Namespaces
ns_health = api.namespace("", description="Health check")
ns_puzzles = api.namespace("api", description="Puzzle operations")

# Modelos para documentación
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
    "Playable", {"grid": fields.Raw, "is_valid": fields.Boolean}
)

solution_model = api.model(
    "Solution", {"grid": fields.Raw, "is_valid": fields.Boolean}
)

difficulty_model = api.model(
    "Difficulty", {"level": fields.String, "coefficient": fields.Float}
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


@ns_health.route("/")
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        return {"status": "ok", "service": "sudoku-api", "version": "2.0.0"}


@ns_puzzles.route("/boards")
class Boards(Resource):
    def get(self):
        """Obtiene resumen de tableros disponibles por dificultad"""
        try:
            boards = puzzle_db.get_boards()
            return {"success": True, "data": boards}, 200
        except Exception as e:
            return {"error": "Failed to retrieve boards", "message": str(e)}, 500


@ns_puzzles.route("/daily")
class DailyPuzzle(Resource):
    @api.doc(
        params={
            "difficulty": {
                "description": "Nivel de dificultad",
                "enum": ["EASY", "MEDIUM", "HARD", "EXPERT", "MASTER"],
                "default": "MEDIUM",
            }
        }
    )
    @api.response(200, "Success", game_response_model)
    def get(self):
        """Obtiene el puzzle del día según dificultad (un puzzle único por día)"""
        try:
            from datetime import date

            difficulty = request.args.get("difficulty", "MEDIUM", type=str)
            today = str(date.today())

            puzzle = puzzle_db.find_daily_puzzle(difficulty, today)

            if not puzzle:
                puzzle = puzzle_db.assign_daily_puzzle(difficulty, today)

            if not puzzle:
                return {
                    "error": "No puzzles available",
                    "message": f"No unassigned puzzles found for difficulty {difficulty}",
                }, 404

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
                        "empty_cells": puzzle["empty_cells"],
                        "is_daily": True,
                        "date_assigned": today,
                    },
                },
            }, 200

        except Exception as e:
            return {"error": "Failed to get daily puzzle", "message": str(e)}, 500


@ns_puzzles.route("/stats")
class Stats(Resource):
    def get(self):
        """Obtiene estadísticas de puzzles disponibles"""
        try:
            return {
                "success": True,
                "data": {
                    "total_puzzles": puzzle_db.count_all_puzzles(),
                    "by_difficulty": puzzle_db.get_boards()["boards"],
                    "daily_assigned": puzzle_db.count_daily_assigned(),
                },
            }, 200
        except Exception as e:
            return {"error": "Failed to get stats", "message": str(e)}, 500


@ns_puzzles.route("/game")
class Game(Resource):
    @api.doc(
        params={
            "iterations": {
                "description": "Número de iteraciones (10-200). Más iteraciones = más difícil",
                "type": "int",
                "default": 70,
            },
            "difficulty": {
                "description": "Nivel de dificultad",
                "enum": ["EASY", "MEDIUM", "HARD", "EXPERT", "MASTER"],
                "default": "MEDIUM",
            },
        }
    )
    @api.response(200, "Success", game_response_model)
    def get(self):
        """Genera un nuevo puzzle de Sudoku (usa caché si existe)"""
        try:
            iterations = request.args.get("iterations", 70, type=int)

            if not 10 <= iterations <= 200:
                return {"error": "Invalid iterations parameter"}, 400

            cached_puzzle = puzzle_db.find_puzzle(
                request.args.get("difficulty", "MEDIUM", type=str)
            )

            if cached_puzzle:
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
                            "empty_cells": cached_puzzle["empty_cells"],
                            "cached": True,
                        },
                    },
                }, 200

            is_complex = iterations > 80

            if not is_complex:
                game = OptimizedSudokuGameGenerator.generate_puzzle(iterations)
                puzzle_db.save_puzzle(game)

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
                            "empty_cells": len(game.playable.get_empty_cells()),
                            "cached": False,
                        },
                    },
                }, 200

        except Exception as e:
            return {"error": "Failed to generate game", "message": str(e)}, 500


@ns_puzzles.route("/validate")
class Validate(Resource):
    @api.expect(grid_model)
    def post(self):
        """Valida un tablero de Sudoku (verifica reglas sin resolver)"""
        try:
            data = request.get_json()

            if not data:
                return {
                    "error": "Invalid JSON",
                    "message": "Request body must be valid JSON",
                }, 400

            if "grid" not in data:
                return {
                    "error": "Missing grid parameter",
                    "message": "grid field is required in request body",
                }, 400

            grid = data["grid"]

            if not isinstance(grid, list) or len(grid) != 9:
                return {
                    "error": "Invalid grid format",
                    "message": "grid must be a 9x9 matrix",
                }, 400

            for i, row in enumerate(grid):
                if not isinstance(row, list) or len(row) != 9:
                    return {
                        "error": "Invalid grid format",
                        "message": f"Row {i} must have exactly 9 elements",
                    }, 400

                for j, cell in enumerate(row):
                    if not isinstance(cell, int) or not 0 <= cell <= 9:
                        return {
                            "error": "Invalid cell value",
                            "message": f"Cell at [{i}][{j}] must be an integer between 0-9",
                        }, 400

            validator = Validator(grid)

            return {
                "success": True,
                "data": {
                    "is_valid": validator.is_valid,
                    "grid": grid,
                    "validation_details": {
                        "total_cells": 81,
                        "filled_cells": sum(
                            1 for row in grid for cell in row if cell != 0
                        ),
                        "empty_cells": sum(
                            1 for row in grid for cell in row if cell == 0
                        ),
                    },
                },
            }, 200

        except Exception as e:
            return {"error": "Validation failed", "message": str(e)}, 500


@ns_puzzles.route("/solve")
class Solve(Resource):
    @api.expect(grid_model)
    def post(self):
        """Resuelve un tablero de Sudoku parcialmente completado"""
        try:
            data = request.get_json()

            if not data or "grid" not in data:
                return {
                    "error": "Invalid request",
                    "message": "grid field is required",
                }, 400

            from sudoku_api.sudoku_board import SudokuBoard
            from sudoku_game import OptimizedSudokuSolver

            board = SudokuBoard(data["grid"])

            if board.is_valid and len(board.get_empty_cells()) == 0:
                return {
                    "success": True,
                    "data": {
                        "solved_grid": board.grid,
                        "message": "Sudoku was already solved",
                    },
                }, 200

            solver = OptimizedSudokuSolver(board)
            solution = solver.solve()

            return {
                "success": True,
                "data": {
                    "original_grid": data["grid"],
                    "solved_grid": solution.grid,
                    "difficulty_coefficient": round(solver.difficult_coefficient, 2),
                    "steps_taken": "Solved successfully",
                },
            }, 200

        except Exception as e:
            return {"error": "Failed to solve", "message": str(e)}, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"Starting Sudoku API on port {port}")
    print(f"Debug mode: {debug}")

    app.run(host="0.0.0.0", port=port, debug=debug)
