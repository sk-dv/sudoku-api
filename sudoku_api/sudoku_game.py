import random

import enum

from sudoku_board import SudokuBoard
from sudoku_solver import SudokuSolver

class DifficultLevel(enum.Enum):
    VERY_EASY = 2
    EASY = 3
    MEDIUM = 5
    HARD = 7
    VERY_HARD = 10
    MASTER = 100


class SudokuGame:
    def __init__(
        self,
        playable: SudokuBoard,
        solution: SudokuBoard,
        difficult_level: DifficultLevel,
        difficult_coefficient: float,
    ):
        self.playable = playable
        self.solution = solution
        self.difficult_level = difficult_level
        self.difficult_coefficient = difficult_coefficient

    def __str__(self):
        print(self.difficult_level.name)
        return (
            "**GAME** \n"
            + "Difficult: "
            + self.difficult_level.name
            + " ("
            + str(self.difficult_coefficient)
            + ")\n"
            + str(self.playable)
        )


class SudokuGameGenerator:
    @staticmethod
    def generate_puzzle(iterations: int = 70) -> SudokuGame:
        solution = SudokuBoard()
        solution.build()

        playable = solution.clone()
        difficult_coefficient = 1
        for _ in range(iterations):
            new_playable = playable.clone()

            row_num, column_num = random.randrange(9), random.randrange(9)
            while new_playable.is_cell_empty(row_num, column_num):
                row_num, column_num = random.randrange(9), random.randrange(9)
            new_playable.clear_cell(row_num, column_num)

            solver = SudokuSolver(new_playable)
            try:
                solver.solve()
                playable = new_playable
                difficult_coefficient = solver.difficult_coefficient
            except:
                continue

        difficult_level = None
        if difficult_coefficient < DifficultLevel.VERY_EASY.value:
            difficult_level = DifficultLevel.VERY_EASY
        elif difficult_coefficient < DifficultLevel.EASY.value:
            difficult_level = DifficultLevel.EASY
        elif difficult_coefficient < DifficultLevel.MEDIUM.value:
            difficult_level = DifficultLevel.MEDIUM
        elif difficult_coefficient < DifficultLevel.HARD.value:
            difficult_level = DifficultLevel.HARD
        elif difficult_coefficient < DifficultLevel.VERY_HARD.value:
            difficult_level = DifficultLevel.VERY_HARD
        elif difficult_coefficient < DifficultLevel.MASTER.value:
            difficult_level = DifficultLevel.MASTER

        return SudokuGame(playable, solution, difficult_level, difficult_coefficient)
