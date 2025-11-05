from flask_restx import Resource
from sudoku_api.database import PuzzleDB


puzzle_db = None


def get_db():
    global puzzle_db
    if puzzle_db is None:
        puzzle_db = PuzzleDB()
    return puzzle_db
