from flask import Flask, request
import os
import sys

# Agregar el directorio sudoku_api al path
sys.path.append(os.path.join(os.path.dirname(__file__), "sudoku_api"))

from sudoku_game import SudokuGameGenerator
from validator import Validator

app = Flask(__name__)

# Configuración
app.config["JSON_SORT_KEYS"] = False


@app.route("/")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "sudoku-api", "version": "1.0.0"}, 200


@app.route("/api/game", methods=["GET"])
def generate_game():
    """
    Genera un nuevo juego de Sudoku
    Query parameters:
    - iterations: número de iteraciones para generar dificultad (10-200, default: 70)
    """
    try:
        # Obtener parámetros
        iterations = request.args.get("iterations", 70, type=int)

        # Validar iterations
        if not 10 <= iterations <= 200:
            return {
                "error": "Invalid iterations parameter",
                "message": "iterations must be between 10 and 200",
                "received": iterations,
            }, 400

        # Generar juego
        game = SudokuGameGenerator.generate_puzzle(iterations)

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
                },
            },
        }, 200

    except Exception as e:
        return {"error": "Failed to generate game", "message": str(e)}, 500


@app.route("/api/validate", methods=["POST"])
def validate_board():
    """
    Valida un tablero de Sudoku
    Body JSON:
    {
        "grid": [[int]] // matriz 9x9 con números 1-9 y 0 para celdas vacías
    }
    """
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

        # Validar formato de grid
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

        # Validar con el Validator
        validator = Validator(grid)

        return {
            "success": True,
            "data": {
                "is_valid": validator.is_valid,
                "grid": grid,
                "validation_details": {
                    "total_cells": 81,
                    "filled_cells": sum(1 for row in grid for cell in row if cell != 0),
                    "empty_cells": sum(1 for row in grid for cell in row if cell == 0),
                },
            },
        }, 200

    except Exception as e:
        return {"error": "Validation failed", "message": str(e)}, 500


@app.route("/api/solve", methods=["POST"])
def solve_board():
    """
    Resuelve un tablero de Sudoku parcialmente completado
    Body JSON:
    {
        "grid": [[int]] // matriz 9x9 con números 1-9 y 0 para celdas vacías
    }
    """
    try:
        data = request.get_json()

        if not data or "grid" not in data:
            return {
                "error": "Invalid request",
                "message": "grid field is required",
            }, 400

        # Importar aquí para evitar importaciones circulares
        from sudoku_board import SudokuBoard
        from sudoku_solver import SudokuSolver

        # Crear board desde la grid recibida
        board = SudokuBoard(data["grid"])

        # Validar que no esté ya resuelto
        if board.is_valid and len(board.get_empty_cells()) == 0:
            return {
                "success": True,
                "data": {
                    "solved_grid": board.grid,
                    "message": "Sudoku was already solved",
                },
            }, 200

        # Resolver
        solver = SudokuSolver(board)
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


@app.errorhandler(404)
def not_found(error):
    return {
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "GET /",
            "GET /api/game",
            "POST /api/validate",
            "POST /api/solve",
        ],
    }, 404


@app.errorhandler(405)
def method_not_allowed(error):
    return {
        "error": "Method not allowed",
        "message": f"Method {request.method} is not allowed for this endpoint",
    }, 405


@app.errorhandler(500)
def internal_server_error(error):
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
    }, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"Starting Sudoku API on port {port}")
    print(f"Debug mode: {debug}")

    app.run(host="0.0.0.0", port=port, debug=debug)
