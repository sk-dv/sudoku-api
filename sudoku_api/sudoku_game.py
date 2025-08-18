import random
import enum
from sudoku_api.sudoku_board import SudokuBoard
from sudoku_api.sudoku_solver import OptimizedSudokuSolver


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
    def generate_puzzle(iterations: int = 70, progress_callback=None) -> SudokuGame:
        """Genera puzzle optimizado con callback opcional de progreso"""
        
        # Progreso inicial
        if progress_callback:
            progress_callback(0, "Iniciando generación...")

        # Generar tablero completo
        solution = SudokuBoard()
        solution.build()
        
        if progress_callback:
            progress_callback(10, "Tablero base creado")

        # Eliminar celdas
        playable = solution.clone()
        successful_removals = 0
        max_empty_cells = min(iterations, 64)

        # Calcular intervalo de reporte (cada 10% aprox)
        report_interval = max(5, iterations // 10)

        for i in range(iterations):
            if successful_removals >= max_empty_cells:
                break

            # Seleccionar celda aleatoria (tu lógica actual)
            row, col = random.randrange(9), random.randrange(9)
            if playable.is_cell_empty(row, col):
                continue

            # Intentar eliminar (tu lógica actual)
            new_playable = playable.clone()
            new_playable.clear_cell(row, col)

            # Verificar solución única (tu lógica actual)
            solver = OptimizedSudokuSolver(new_playable)
            try:
                solver.solve()
                playable = new_playable
                successful_removals += 1
            except:
                continue

            # Reportar progreso periódicamente
            if progress_callback and (i % report_interval == 0 or i == iterations - 1):
                progress = int(10 + (i / iterations) * 80)  # 10% a 90%
                progress_callback(
                    progress, 
                    f"Eliminando celdas: {successful_removals} exitosas de {i+1} intentadas"
                )

        # Calcular dificultad final
        if progress_callback:
            progress_callback(95, "Calculando dificultad final...")
            
        final_solver = OptimizedSudokuSolver(playable)
        try:
            final_solver.solve()
            difficult_coefficient = final_solver.improved_coefficient
        except:
            difficult_coefficient = 5.0

        # Determinar nivel (tu lógica actual)
        difficult_level = OptimizedSudokuGameGenerator._calculate_difficulty_level(
            difficult_coefficient
        )

        if progress_callback:
            progress_callback(100, "Generación completada")

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
