import random
from sudoku_api.sudoku_board import SudokuBoard
from sudoku_api.sudoku_solver import OptimizedSudokuSolver
from sudoku_api.enums import DifficultyLevel


class SudokuGame:
    def __init__(
        self,
        playable: SudokuBoard,
        solution: SudokuBoard,
        difficult_level: DifficultyLevel,
        difficult_coefficient: float,
    ):
        self.playable = playable
        self.solution = solution
        self.difficult_level = difficult_level
        self.difficult_coefficient = difficult_coefficient


class OptimizedSudokuGameGenerator:
    _ITERATION_RANGES = {
        DifficultyLevel.BEGINNER:    (15, 30),
        DifficultyLevel.EASY:        (30, 45),
        DifficultyLevel.MEDIUM:      (45, 60),
        DifficultyLevel.HARD:        (60, 80),
        DifficultyLevel.EXPERT:      (80, 110),
        DifficultyLevel.MASTER:      (110, 150),
        DifficultyLevel.GRANDMASTER: (150, 200),
    }

    @staticmethod
    def generate_puzzle(
        target_level: DifficultyLevel = None,
        iterations: int = None,
        progress_callback=None,
    ) -> SudokuGame:
        """Genera puzzle optimizado con callback opcional de progreso.

        Si se pasa target_level, el número de iteraciones se deriva del rango
        correspondiente y se reintenta hasta 3 veces si el coeficiente resultante
        no cae dentro del rango esperado.
        """
        if target_level is None:
            target_level = DifficultyLevel.get_default()

        max_attempts = 3
        for attempt in range(max_attempts):
            if progress_callback:
                progress_callback(0, f"Iniciando generación (intento {attempt + 1})...")

            if iterations is not None:
                iter_count = iterations
            else:
                min_iter, max_iter = OptimizedSudokuGameGenerator._ITERATION_RANGES[target_level]
                iter_count = random.randint(min_iter, max_iter)

            game = OptimizedSudokuGameGenerator._generate_once(iter_count, progress_callback)

            if game.difficult_level == target_level:
                return game

            # Si es el último intento, devolver lo que tenemos
            if attempt == max_attempts - 1:
                return game

        return game  # fallback (nunca alcanzado)

    @staticmethod
    def _generate_once(iterations: int, progress_callback=None) -> SudokuGame:
        if progress_callback:
            progress_callback(10, "Tablero base creado")

        solution = SudokuBoard()
        solution.build()

        playable = solution.clone()
        successful_removals = 0
        max_empty_cells = min(iterations, 64)
        report_interval = max(5, iterations // 10)

        for i in range(iterations):
            if successful_removals >= max_empty_cells:
                break

            row, col = random.randrange(9), random.randrange(9)
            if playable.is_cell_empty(row, col):
                continue

            new_playable = playable.clone()
            new_playable.clear_cell(row, col)

            solver = OptimizedSudokuSolver(new_playable)
            try:
                solver.solve()
                playable = new_playable
                successful_removals += 1
            except Exception:
                continue

            if progress_callback and (i % report_interval == 0 or i == iterations - 1):
                progress = int(10 + (i / iterations) * 80)
                progress_callback(
                    progress,
                    f"Eliminando celdas: {successful_removals} exitosas de {i+1} intentadas",
                )

        if progress_callback:
            progress_callback(95, "Calculando dificultad final...")

        final_solver = OptimizedSudokuSolver(playable)
        try:
            final_solver.solve()
            difficult_coefficient = final_solver.improved_coefficient
        except Exception:
            difficult_coefficient = 5.0

        difficult_level = DifficultyLevel.from_coefficient(difficult_coefficient)

        if progress_callback:
            progress_callback(100, "Generación completada")

        return SudokuGame(playable, solution, difficult_level, difficult_coefficient)
