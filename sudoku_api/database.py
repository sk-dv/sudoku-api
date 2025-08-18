import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor


class PuzzleDB:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")

    def get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)

    def save_puzzle(self, game):
        """Guardar puzzle en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO puzzles (difficulty, empty_cells, playable_grid, solution_grid, coefficient)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        game.difficult_level.name,
                        len(game.playable.get_empty_cells()),
                        json.dumps(game.playable.grid),
                        json.dumps(game.solution.grid),
                        game.difficult_coefficient,
                    ),
                )
                conn.commit()

    def find_puzzle(self, difficulty, target_empty_cells):
        """Buscar puzzle similar en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Buscar con rango ±5 celdas
                cur.execute(
                    """
                    SELECT * FROM puzzles 
                    WHERE difficulty = %s 
                    AND empty_cells BETWEEN %s AND %s
                    ORDER BY RANDOM() 
                    LIMIT 1
                """,
                    (difficulty, target_empty_cells - 5, target_empty_cells + 5),
                )

                return cur.fetchone()

    def count_puzzles(self, difficulty):
        """Contar puzzles disponibles"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as count FROM puzzles WHERE difficulty = %s",
                    (difficulty,),
                )
                return cur.fetchone()["count"]
