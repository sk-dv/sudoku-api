from flask_restx import Resource
from flask import request
from sudoku_api.validator import Validator


class ValidateResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data or "grid" not in data:
                return {"error": "Missing grid parameter"}, 400

            grid = data["grid"]

            if not isinstance(grid, list) or len(grid) != 9:
                return {"error": "Invalid grid format"}, 400

            for i, row in enumerate(grid):
                if not isinstance(row, list) or len(row) != 9:
                    return {"error": f"Row {i} must have 9 elements"}, 400

                for j, cell in enumerate(row):
                    if not isinstance(cell, int) or not 0 <= cell <= 9:
                        return {"error": f"Invalid cell at [{i}][{j}]"}, 400

            validator = Validator(grid)
            filled = sum(1 for row in grid for cell in row if cell != 0)
            empty = 81 - filled

            return {
                "success": True,
                "data": {
                    "is_valid": validator.is_valid,
                    "grid": grid,
                    "validation_details": {
                        "total_cells": 81,
                        "filled_cells": filled,
                        "empty_cells": empty,
                    },
                },
            }, 200

        except Exception as e:
            return {"error": "Validation failed", "message": str(e)}, 500
