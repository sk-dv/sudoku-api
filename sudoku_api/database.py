import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor


class PuzzleDB:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")

    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)

    def find_puzzle(self, difficulty):
        """Buscar puzzle similar en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Buscar con rango ±5 celdas
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
            
    def get_boards(self):
        """Obtiene todos los tableros de Sudoku y un mapa de cuántos hay por dificultad"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Obtener el conteo por dificultad
                cur.execute("SELECT difficulty, COUNT(*) as count FROM puzzles GROUP BY difficulty")
                counts = {row['difficulty']: row['count'] for row in cur.fetchall()}
                return {"boards": counts}

    def count_all_puzzles(self):
        """Contar todos los puzzles en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM puzzles")
                return cur.fetchone()["count"]
