from flask_restx import Resource
from flask import request
from sudoku_api.sudoku_board import SudokuBoard
from sudoku_api.sudoku_solver import OptimizedSudokuSolver


class SolveResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data or "grid" not in data:
                return {"error": "grid field is required"}, 400

            board = SudokuBoard(data["grid"])

            if board.is_valid and len(board.get_empty_cells()) == 0:
                return {
                    "success": True,
                    "data": {
                        "solved_grid": board.grid,
                        "message": "Already solved",
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
                },
            }, 200

        except Exception as e:
            return {"error": "Failed to solve", "message": str(e)}, 500
