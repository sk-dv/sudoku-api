import logging
from flask_restx import Resource
from flask import request
from sudoku_api.validator import Validator, validate_grid_format

logger = logging.getLogger(__name__)


class ValidateResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data or "grid" not in data:
                return {"error": "Missing grid parameter"}, 400

            grid = data["grid"]

            error = validate_grid_format(grid)
            if error:
                return {"error": error}, 400

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

        except Exception:
            logger.exception("Validation failed")
            return {"error": "Validation failed"}, 500
