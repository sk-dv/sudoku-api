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

    def count_puzzles(self, difficulty):
        """Contar puzzles disponibles"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as count FROM puzzles WHERE difficulty = %s",
                    (difficulty,),
                )
                return cur.fetchone()["count"]
            
    def get_boards(self):
        """Obtiene todos los tableros de Sudoku y un mapa de cuántos hay por dificultad"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Obtener el conteo por dificultad
                cur.execute("SELECT difficulty, COUNT(*) as count FROM puzzles GROUP BY difficulty")
                counts = {row['difficulty']: row['count'] for row in cur.fetchall()}
                return {"boards": counts}

    def find_daily_puzzle(self, difficulty, date):
        """Buscar puzzle asignado para una fecha específica"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM puzzles
                    WHERE difficulty = %s AND date_assigned = %s
                    LIMIT 1
                    """,
                    (difficulty, date),
                )
                return cur.fetchone()

    def assign_daily_puzzle(self, difficulty, date):
        """Asignar un puzzle random para el día"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Actualizar un puzzle random con la fecha
                cur.execute(
                    """
                    UPDATE puzzles
                    SET date_assigned = %s
                    WHERE id = (
                        SELECT id FROM puzzles
                        WHERE difficulty = %s AND date_assigned IS NULL
                        ORDER BY RANDOM() LIMIT 1
                    )
                    RETURNING *
                    """,
                    (date, difficulty),
                )
                conn.commit()
                return cur.fetchone()

    def count_all_puzzles(self):
        """Contar todos los puzzles en BD"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM puzzles")
                return cur.fetchone()["count"]

    def count_daily_assigned(self):
        """Contar puzzles asignados a fechas"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM puzzles WHERE date_assigned IS NOT NULL")
                return cur.fetchone()["count"]
