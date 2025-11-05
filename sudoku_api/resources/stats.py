from flask_restx import Resource
from sudoku_api.resources import get_db


class StatsResource(Resource):
    def get(self):
        try:
            db = get_db()
            boards_data = db.get_boards()
            
            return {
                "success": True,
                "data": {
                    "total_puzzles": db.count_all_puzzles(),
                    "counts_by_difficulty": boards_data.get("counts_by_difficulty", {}),
                    "daily_assigned": db.count_daily_assigned(),
                },
            }, 200
        except Exception as e:
            return {"error": "Failed to get stats", "message": str(e)}, 500
