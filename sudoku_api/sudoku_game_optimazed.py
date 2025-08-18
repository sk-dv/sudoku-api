import random
import enum
from sudoku_api.sudoku_board import SudokuBoard
from sudoku_api.sudoku_solver_optimized import OptimizedSudokuSolver


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


class OptimizedSudokuGameGenerator:
    @staticmethod
    def generate_puzzle(iterations: int = 70) -> SudokuGame:
        """Genera puzzle optimizado simple"""
        # Generar tablero completo
        solution = SudokuBoard()
        solution.build()

        # Eliminar celdas
        playable = solution.clone()
        successful_removals = 0
        max_empty_cells = min(iterations, 64)

        for i in range(iterations):
            if successful_removals >= max_empty_cells:
                break

            # Seleccionar celda aleatoria
            row, col = random.randrange(9), random.randrange(9)
            if playable.is_cell_empty(row, col):
                continue

            # Intentar eliminar
            new_playable = playable.clone()
            new_playable.clear_cell(row, col)

            # Verificar solución única
            solver = OptimizedSudokuSolver(new_playable)
            try:
                solver.solve()
                playable = new_playable
                successful_removals += 1
            except:
                continue

        # Calcular dificultad final
        final_solver = OptimizedSudokuSolver(playable)
        try:
            final_solver.solve()
            difficult_coefficient = final_solver.improved_coefficient
        except:
            difficult_coefficient = 5.0

        # Determinar nivel
        difficult_level = OptimizedSudokuGameGenerator._calculate_difficulty_level(
            difficult_coefficient
        )

        return SudokuGame(playable, solution, difficult_level, difficult_coefficient)

    @staticmethod
    def _calculate_difficulty_level(coefficient: float) -> DifficultLevel:
        """Umbrales simplificados"""
        if coefficient < 3.0:
            return DifficultLevel.VERY_EASY
        elif coefficient < 4.5:
            return DifficultLevel.EASY
        elif coefficient < 6.0:
            return DifficultLevel.MEDIUM
        elif coefficient < 7.5:
            return DifficultLevel.HARD
        elif coefficient < 8.5:
            return DifficultLevel.VERY_HARD
        else:
            return DifficultLevel.MASTER
