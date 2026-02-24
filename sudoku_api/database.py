import os
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

    def find_puzzle(self, difficulty):
        """Buscar puzzle similar en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM puzzles
                    WHERE difficulty = %s
                    ORDER BY RANDOM()
                    LIMIT 1
                """,
                    (difficulty,),
                )
                return cur.fetchone()

    def find_daily_puzzle(self, date):
        """Buscar puzzle asignado a una fecha específica"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM puzzles WHERE date_assigned = %s LIMIT 1",
                    (date,),
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