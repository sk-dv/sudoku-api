from flask import Flask, request, Response, jsonify
from flask_cors import CORS

import os
import json
import time


from sudoku_api.sudoku_game_optimazed import OptimizedSudokuGameGenerator
from sudoku_api.sudoku_game import SudokuGameGenerator
from sudoku_api.validator import Validator

app = Flask(__name__)
CORS(app)  # Habilitar CORS para multiplataforma

# Configuración
app.config["JSON_SORT_KEYS"] = False


@app.route("/")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "sudoku-api", "version": "2.0.0"}, 200


@app.route("/api/game", methods=["GET"])
def generate_game():
    """
    Genera un nuevo juego de Sudoku (versión original)
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


@app.route("/api/game/stream", methods=["GET"])
def generate_game_with_progress():
    """
    Genera un nuevo juego de Sudoku con progreso en tiempo real vía SSE
    Query parameters:
    - iterations: número de iteraciones (10-200, default: 70)
    """
    iterations = request.args.get("iterations", 70, type=int)

    # Validar iterations
    if not 10 <= iterations <= 200:
        return (
            jsonify(
                {
                    "error": "Invalid iterations parameter",
                    "message": "iterations must be between 10 and 200",
                }
            ),
            400,
        )

    def generate():
        """Generador de eventos SSE"""
        try:
            # Enviar evento inicial
            yield f"data: {json.dumps({'progress': 0, 'status': 'initializing', 'message': 'Creando tablero base...'})}\n\n"

            # Usar el generador optimizado con callback de progreso
            def progress_callback(current, total, message="", partial_grid=None):
                progress_data = {
                    "progress": round((current / total) * 100, 1),
                    "current": current,
                    "total": total,
                    "status": "processing",
                    "message": message,
                }

                # Incluir grid parcial si está disponible (opcional)
                if partial_grid:
                    progress_data["partial_grid"] = partial_grid

                return f"data: {json.dumps(progress_data)}\n\n"

            # Generar el juego con progreso
            generator = OptimizedSudokuGameGenerator()

            # Stream de actualizaciones durante la generación
            for update in generator.generate_puzzle_with_progress(
                iterations, progress_callback
            ):
                yield update
                time.sleep(0.01)  # Pequeña pausa para no saturar

            # Obtener el juego final
            game = generator.get_final_game()

            # Enviar resultado final
            final_data = {
                "progress": 100,
                "status": "completed",
                "message": "Juego generado exitosamente",
                "game": {
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
            }

            yield f"data: {json.dumps(final_data)}\n\n"

        except Exception as e:
            error_data = {
                "progress": -1,
                "status": "error",
                "message": f"Error generando juego: {str(e)}",
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Desactivar buffering en nginx
            "Connection": "keep-alive",
        },
    )


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
        from sudoku_api.sudoku_board import SudokuBoard
        from sudoku_api.sudoku_game_optimazed import OptimizedSudokuSolver

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

        # Resolver con el solver optimizado
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


@app.errorhandler(404)
def not_found(error):
    return {
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "GET /",
            "GET /api/game",
            "GET /api/game/stream",
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
    print("New endpoints available:")
    print("  - GET /api/game/stream for real-time progress")

    app.run(host="0.0.0.0", port=port, debug=debug)
