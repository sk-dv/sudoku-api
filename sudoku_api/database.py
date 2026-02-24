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