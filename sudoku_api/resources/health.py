from flask_restx import Resource


class HealthResource(Resource):
    def get(self):
        """Health check endpoint"""
        return {
            "status": "ok",
            "service": "sudoku-api",
            "version": "2.0.0"
        }, 200
