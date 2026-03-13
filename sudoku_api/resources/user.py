import logging
from flask import g
from flask_restx import Resource
from sudoku_api.auth import require_firebase_auth
from sudoku_api.resources import get_db

logger = logging.getLogger(__name__)


class AuthRegisterResource(Resource):
    @require_firebase_auth
    def post(self):
        """Crea o actualiza el perfil del usuario autenticado con Firebase."""
        try:
            db = get_db()
            user = db.get_or_create_user(
                firebase_uid=g.firebase_uid,
                email=g.firebase_email,
                display_name=g.firebase_name,
            )
            return {"success": True, "data": {"user": _serialize_user(user)}}, 200
        except Exception:
            logger.exception("Failed to register user")
            return {"error": "Failed to register user"}, 500


class UserStatsResource(Resource):
    @require_firebase_auth
    def get(self):
        """Estadísticas del usuario autenticado."""
        try:
            db = get_db()
            stats = db.get_user_stats(g.firebase_uid)
            if stats is None:
                return {"success": True, "data": {"stats": None}}, 200
            return {"success": True, "data": {"stats": _serialize_stats(stats)}}, 200
        except Exception:
            logger.exception("Failed to get user stats")
            return {"error": "Failed to get user stats"}, 500


class ProgressSaveResource(Resource):
    @require_firebase_auth
    def post(self):
        """Guarda el progreso de una partida."""
        from flask import request
        body = request.get_json(silent=True) or {}

        puzzle_id = body.get("puzzle_id")
        current_state = body.get("current_state")
        time_elapsed = body.get("time_elapsed", 0)
        hints_used = body.get("hints_used", 0)
        completed = bool(body.get("completed", False))

        if puzzle_id is None or current_state is None:
            return {"error": "puzzle_id and current_state are required"}, 400

        try:
            db = get_db()
            progress = db.save_progress(
                user_id=g.firebase_uid,
                puzzle_id=puzzle_id,
                current_state=current_state,
                time_elapsed=time_elapsed,
                hints_used=hints_used,
                completed=completed,
            )
            if completed:
                puzzle = db.find_puzzle_by_id(puzzle_id)
                if puzzle:
                    db.update_user_stats(
                        user_id=g.firebase_uid,
                        completed=True,
                        difficulty=puzzle["difficulty"],
                        time_seconds=time_elapsed,
                    )
            return {"success": True, "data": {"progress": _serialize_progress(progress)}}, 200
        except Exception:
            logger.exception("Failed to save progress")
            return {"error": "Failed to save progress"}, 500


def _serialize_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "is_premium": row["is_premium"],
        "created_at": str(row["created_at"]),
        "last_active": str(row["last_active"]),
    }


def _serialize_stats(row: dict) -> dict:
    return {
        "games_played": row["games_played"],
        "games_completed": row["games_completed"],
        "best_times": row["best_times"],
        "current_streak": row["current_streak"],
        "best_streak": row["best_streak"],
        "updated_at": str(row["updated_at"]),
    }


def _serialize_progress(row: dict) -> dict:
    return {
        "puzzle_id": row["puzzle_id"],
        "time_elapsed": row["time_elapsed"],
        "hints_used": row["hints_used"],
        "completed": row["completed"],
        "completed_at": str(row["completed_at"]) if row["completed_at"] else None,
    }
