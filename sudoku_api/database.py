import os
import random
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


class PuzzleDB:
    def __init__(self):
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise EnvironmentError("DATABASE_URL no está configurada")
        self._pool = psycopg2.pool.ThreadedConnectionPool(
            1, 10, database_url, cursor_factory=RealDictCursor
        )

    @contextmanager
    def get_connection(self):
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def find_puzzle_by_id(self, puzzle_id: int) -> dict | None:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM puzzles WHERE id = %s", (puzzle_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def find_puzzle(self, difficulty):
        """Buscar puzzle aleatorio por dificultad sin full table scan"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as count FROM puzzles WHERE difficulty = %s",
                    (difficulty,),
                )
                count = cur.fetchone()["count"]
                if count == 0:
                    return None
                offset = random.randint(0, count - 1)
                cur.execute(
                    "SELECT * FROM puzzles WHERE difficulty = %s LIMIT 1 OFFSET %s",
                    (difficulty, offset),
                )
                return cur.fetchone()

    def find_daily_puzzle(self, difficulty: str, day_of_year: int):
        """Selecciona el puzzle del día de forma determinística por fecha y dificultad"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as count FROM puzzles WHERE difficulty = %s",
                    (difficulty,),
                )
                count = cur.fetchone()["count"]
                if count == 0:
                    return None
                offset = day_of_year % count
                cur.execute(
                    "SELECT * FROM puzzles WHERE difficulty = %s ORDER BY id LIMIT 1 OFFSET %s",
                    (difficulty, offset),
                )
                return cur.fetchone()

    def get_boards(self):
        """Obtiene todos los tableros de Sudoku y un mapa de cuántos hay por dificultad"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT difficulty, COUNT(*) as count FROM puzzles GROUP BY difficulty")
                counts = {row['difficulty']: row['count'] for row in cur.fetchall()}
                return {"boards": counts}

    def count_all_puzzles(self):
        """Contar todos los puzzles en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM puzzles")
                return cur.fetchone()["count"]

    # --- Usuarios ---

    def get_or_create_user(self, firebase_uid: str, email: str, display_name: str) -> dict:
        """Devuelve el usuario existente o lo crea. Actualiza last_active siempre."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, email, display_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                      SET last_active = NOW(),
                          email = EXCLUDED.email,
                          display_name = EXCLUDED.display_name
                    RETURNING *
                    """,
                    (firebase_uid, email, display_name),
                )
                return dict(cur.fetchone())

    def get_user(self, firebase_uid: str) -> dict | None:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (firebase_uid,))
                row = cur.fetchone()
                return dict(row) if row else None

    # --- Progreso de partidas ---

    def save_progress(
        self,
        user_id: str,
        puzzle_id: int,
        current_state: list,
        time_elapsed: int,
        hints_used: int,
        completed: bool,
    ) -> dict:
        """Upsert del progreso de una partida."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO game_progress
                        (user_id, puzzle_id, current_state, time_elapsed, hints_used, completed, completed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CASE WHEN %s THEN NOW() ELSE NULL END)
                    ON CONFLICT (user_id, puzzle_id) DO UPDATE
                      SET current_state = EXCLUDED.current_state,
                          time_elapsed   = EXCLUDED.time_elapsed,
                          hints_used     = EXCLUDED.hints_used,
                          completed      = EXCLUDED.completed,
                          completed_at   = CASE WHEN EXCLUDED.completed THEN NOW()
                                                ELSE game_progress.completed_at END
                    RETURNING *
                    """,
                    (user_id, puzzle_id, current_state, time_elapsed, hints_used, completed, completed),
                )
                return dict(cur.fetchone())

    # --- Estadísticas de usuario ---

    def get_user_stats(self, user_id: str) -> dict | None:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM user_stats WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def update_user_stats(
        self,
        user_id: str,
        completed: bool,
        difficulty: str,
        time_seconds: int,
    ) -> dict:
        """Actualiza stats tras completar (o guardar) una partida."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_stats (user_id) VALUES (%s)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    (user_id,),
                )
                cur.execute(
                    """
                    UPDATE user_stats
                    SET games_played    = games_played + 1,
                        games_completed = games_completed + CASE WHEN %s THEN 1 ELSE 0 END,
                        best_times      = CASE
                            WHEN %s AND (
                                best_times->%s IS NULL
                                OR (best_times->>%s)::int > %s
                            )
                            THEN jsonb_set(best_times, ARRAY[%s], to_jsonb(%s))
                            ELSE best_times
                        END,
                        updated_at      = NOW()
                    WHERE user_id = %s
                    RETURNING *
                    """,
                    (
                        completed,
                        completed, difficulty, difficulty, time_seconds, difficulty, time_seconds,
                        user_id,
                    ),
                )
                return dict(cur.fetchone())