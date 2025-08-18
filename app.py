from flask import Flask, request, Response
from flask_cors import CORS
import random

import os
import json

from sudoku_api.database import PuzzleDB
from sudoku_api.sudoku_game import OptimizedSudokuGameGenerator
from sudoku_api.validator import Validator

puzzle_db = PuzzleDB()

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
    try:
        iterations = request.args.get("iterations", 70, type=int)

        if not 10 <= iterations <= 200:
            return {"error": "Invalid iterations parameter"}, 400

        # Estimar dificultad y celdas vacías (tu lógica actual)
        target_empty = int(iterations * 0.6)
        estimated_difficulty = "MEDIUM"
        if target_empty < 35:
            estimated_difficulty = "EASY"
        elif target_empty > 55:
            estimated_difficulty = "HARD"

        # Buscar en BD primero (tu lógica actual)
        cached_puzzle = puzzle_db.find_puzzle(estimated_difficulty, target_empty)

        if cached_puzzle:
            # Respuesta desde BD - JSON inmediato
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

        # No existe en BD - decidir estrategia
        is_complex = iterations > 80  # Umbral de complejidad

        if not is_complex:
            # Generación rápida - JSON normal
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
        else:
            # Generación compleja - SSE con progreso
            return generate_complex_with_sse(iterations)

    except Exception as e:
        return {"error": "Failed to generate game", "message": str(e)}, 500


def generate_complex_with_sse(iterations):
    """Genera puzzle complejo con progreso SSE"""

    def generate():
        try:
            # Lista para almacenar mensajes de progreso
            progress_messages = []

            def progress_callback(progress, message):
                progress_data = {
                    "progress": progress,
                    "status": "processing" if progress < 100 else "completed",
                    "message": message,
                }
                progress_messages.append(f"data: {json.dumps(progress_data)}\n\n")

            # Generar usando tu generador optimizado
            game = OptimizedSudokuGameGenerator.generate_puzzle(
                iterations, progress_callback
            )

            # Enviar todos los mensajes de progreso acumulados
            for msg in progress_messages[:-1]:  # Todos menos el último
                yield msg

            # Guardar en BD
            puzzle_db.save_puzzle(game)

            # Mensaje final con el juego completo
            yield f"data: {json.dumps({
                'progress': 100,
                'status': 'completed',
                'message': 'Juego generado exitosamente',
                'data': {
                    'playable': {
                        'grid': game.playable.grid,
                        'is_valid': game.playable.is_valid,
                    },
                    'solution': {
                        'grid': game.solution.grid,
                        'is_valid': game.solution.is_valid,
                    },
                    'difficulty': {
                        'level': game.difficult_level.name,
                        'coefficient': round(game.difficult_coefficient, 2),
                    },
                    'metadata': {
                        'iterations_used': iterations,
                        'empty_cells': len(game.playable.get_empty_cells()),
                        'cached': False,
                    },
                }
            })}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({
                'progress': 0,
                'status': 'error',
                'message': f'Error: {str(e)}'
            })}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


def generate_complex_with_progress(iterations):
    """SSE para generaciones complejas"""

    def generate():
        try:
            # Progreso inicial
            yield f"data: {json.dumps({'progress': 0, 'status': 'initializing', 'message': 'Creando tablero base...'})}\n\n"

            # Generar con reportes de progreso
            game = generate_with_progress_reports(iterations, generate)

            # Guardar en BD
            puzzle_db.save_puzzle(game)

            # Resultado final
            yield f"data: {json.dumps({
                'progress': 100,
                'status': 'completed',
                'message': 'Juego generado exitosamente',
                'data': {
                    'playable': {'grid': game.playable.grid, 'is_valid': game.playable.is_valid},
                    'solution': {'grid': game.solution.grid, 'is_valid': game.solution.is_valid},
                    'difficulty': {'level': game.difficult_level.name, 'coefficient': round(game.difficult_coefficient, 2)},
                    'metadata': {'iterations_used': iterations, 'empty_cells': len(game.playable.get_empty_cells()), 'cached': False}
                }
            })}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'progress': 0, 'status': 'error', 'message': f'Error: {str(e)}'})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
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
        from sudoku_game import OptimizedSudokuSolver

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


def generate_with_progress_reports(iterations, generator_func):
    """Genera puzzle reportando progreso cada cierto número de iteraciones"""
    from sudoku_api.sudoku_game_optimazed import OptimizedSudokuGameGenerator

    # Crear tablero base
    solution = SudokuBoard()
    solution.build()

    generator_func(
        f"data: {json.dumps({'progress': 10, 'status': 'processing', 'message': 'Tablero base creado'})}\n\n"
    )

    playable = solution.clone()
    difficult_coefficient = 1
    successful_removals = 0

    # Reportar progreso cada 10 iteraciones o 10%
    report_interval = max(10, iterations // 10)

    for i in range(iterations):
        new_playable = playable.clone()

        # Encontrar celda no vacía
        row_num, column_num = random.randrange(9), random.randrange(9)
        while new_playable.is_cell_empty(row_num, column_num):
            row_num, column_num = random.randrange(9), random.randrange(9)
        new_playable.clear_cell(row_num, column_num)

        # Validar solución
        solver = SudokuSolver(new_playable)
        try:
            solver.solve()
            playable = new_playable
            difficult_coefficient = solver.difficult_coefficient
            successful_removals += 1
        except:
            continue

        # Reportar progreso
        if i % report_interval == 0 or i == iterations - 1:
            progress = int(10 + (i / iterations) * 85)  # 10% a 95%
            generator_func(
                f"data: {json.dumps({
                'progress': progress, 
                'status': 'processing', 
                'message': f'Eliminando celdas: {successful_removals} de {iterations} intentadas'
            })}\n\n"
            )

    generator_func(
        f"data: {json.dumps({'progress': 95, 'status': 'processing', 'message': 'Calculando dificultad final...'})}\n\n"
    )

    # Calcular nivel de dificultad (tu código actual)
    from sudoku_api.sudoku_game import DifficultLevel, SudokuGame

    if difficult_coefficient < DifficultLevel.VERY_EASY.value:
        difficult_level = DifficultLevel.VERY_EASY
    elif difficult_coefficient < DifficultLevel.EASY.value:
        difficult_level = DifficultLevel.EASY
    elif difficult_coefficient < DifficultLevel.MEDIUM.value:
        difficult_level = DifficultLevel.MEDIUM
    elif difficult_coefficient < DifficultLevel.HARD.value:
        difficult_level = DifficultLevel.HARD
    elif difficult_coefficient < DifficultLevel.VERY_HARD.value:
        difficult_level = DifficultLevel.VERY_HARD
    else:
        difficult_level = DifficultLevel.MASTER

    return SudokuGame(playable, solution, difficult_level, difficult_coefficient)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"Starting Sudoku API on port {port}")
    print(f"Debug mode: {debug}")

    app.run(host="0.0.0.0", port=port, debug=debug)
