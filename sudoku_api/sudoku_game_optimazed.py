import random
import enum
from typing import Callable, Generator, Optional, Tuple, List

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
    # Orden optimizado de eliminación (patrón espiral desde el centro)
    SMART_ELIMINATION_ORDER = [
        # Centro
        (4, 4),
        # Cruz central
        (4, 2),
        (4, 6),
        (2, 4),
        (6, 4),
        # Diagonales del centro
        (2, 2),
        (2, 6),
        (6, 2),
        (6, 6),
        # Bordes centrales
        (0, 4),
        (4, 0),
        (8, 4),
        (4, 8),
        # Esquinas
        (0, 0),
        (0, 8),
        (8, 0),
        (8, 8),
        # Resto en espiral
        (1, 1),
        (1, 7),
        (7, 1),
        (7, 7),
        (3, 3),
        (3, 5),
        (5, 3),
        (5, 5),
        (1, 4),
        (7, 4),
        (4, 1),
        (4, 7),
        (0, 2),
        (0, 6),
        (8, 2),
        (8, 6),
        (2, 0),
        (6, 0),
        (2, 8),
        (6, 8),
    ]

    def __init__(self):
        self.final_game = None
        self._cells_removed = set()

    def get_final_game(self) -> SudokuGame:
        """Retorna el juego final generado"""
        return self.final_game

    def _get_elimination_candidates(
        self, iteration: int, playable: SudokuBoard
    ) -> List[Tuple[int, int]]:
        """
        Obtiene candidatos para eliminación basado en la iteración actual
        """
        candidates = []

        # Primero usar el orden inteligente
        if iteration < len(self.SMART_ELIMINATION_ORDER):
            row, col = self.SMART_ELIMINATION_ORDER[iteration]
            if (row, col) not in self._cells_removed and not playable.is_cell_empty(
                row, col
            ):
                candidates.append((row, col))

        # Si no hay candidatos del orden inteligente, buscar celdas llenas
        if not candidates:
            all_cells = [(r, c) for r in range(9) for c in range(9)]
            # Mezclar para añadir algo de aleatoriedad
            random.shuffle(all_cells)

            for row, col in all_cells:
                if (row, col) not in self._cells_removed and not playable.is_cell_empty(
                    row, col
                ):
                    candidates.append((row, col))
                    if len(candidates) >= 5:  # Limitar candidatos para eficiencia
                        break

        return candidates

    def _quick_uniqueness_check(
        self, board: SudokuBoard, row: int, col: int, original_value: int
    ) -> bool:
        """
        Verificación rápida de unicidad sin resolver completamente
        Retorna True si parece tener solución única
        """
        # Contar cuántas opciones hay para esta celda
        available = board.get_available_numbers(row, col)

        # Si solo hay una opción, definitivamente es única
        if len(available) == 1:
            return True

        # Si hay muchas opciones, probablemente no es única
        if len(available) > 3:
            return False

        # Para 2-3 opciones, hacer verificación más profunda
        # Verificar si alguna otra opción lleva a contradicción rápida
        for num in available:
            if num != original_value:
                test_board = board.clone()
                test_board.assign(row, col, num)

                # Verificar si hay celdas sin opciones (contradicción rápida)
                empty_cells = test_board.get_empty_cells()
                for er, ec in empty_cells[:5]:  # Solo verificar primeras 5 celdas
                    if len(test_board.get_available_numbers(er, ec)) == 0:
                        return True  # Esta opción falla, así que probablemente única

        return True  # Asumir única si no encontramos problemas obvios

    def generate_puzzle_with_progress(
        self, iterations: int = 70, progress_callback: Optional[Callable] = None
    ) -> Generator[str, None, None]:
        """
        Genera un puzzle con actualizaciones de progreso vía SSE
        """
        # Fase 1: Generar tablero completo
        if progress_callback:
            yield progress_callback(0, iterations + 10, "Generando tablero completo...")

        solution = SudokuBoard()
        solution.build()

        if progress_callback:
            yield progress_callback(10, iterations + 10, "Tablero base completado")

        # Fase 2: Eliminación inteligente
        playable = solution.clone()
        self._cells_removed = set()
        difficult_coefficient = 1.0
        successful_removals = 0
        max_empty_cells = min(iterations, 64)  # Máximo 64 celdas vacías

        for i in range(iterations):
            if progress_callback:
                message = f"Eliminando celdas: {successful_removals}/{max_empty_cells}"
                yield progress_callback(10 + i, iterations + 10, message)

            # Obtener candidatos para eliminación
            candidates = self._get_elimination_candidates(i, playable)

            if not candidates or successful_removals >= max_empty_cells:
                break

            # Intentar eliminar cada candidato
            success = False
            for row, col in candidates:
                original_value = playable.grid[row][col]

                # Crear copia y eliminar celda
                new_playable = playable.clone()
                new_playable.clear_cell(row, col)

                # Verificación rápida de unicidad
                if self._quick_uniqueness_check(new_playable, row, col, original_value):
                    # Hacer verificación completa solo cada 5 eliminaciones
                    if successful_removals % 5 == 0:
                        solver = OptimizedSudokuSolver(new_playable)
                        try:
                            solver.solve()
                            playable = new_playable
                            difficult_coefficient = solver.difficult_coefficient
                            self._cells_removed.add((row, col))
                            successful_removals += 1
                            success = True
                            break
                        except:
                            continue
                    else:
                        # Confiar en la verificación rápida
                        playable = new_playable
                        self._cells_removed.add((row, col))
                        successful_removals += 1
                        success = True
                        break

            # Si no pudimos eliminar ningún candidato, intentar con celda aleatoria
            if not success and successful_removals < max_empty_cells:
                for _ in range(3):  # Máximo 3 intentos aleatorios
                    row, col = random.randrange(9), random.randrange(9)
                    if (
                        not playable.is_cell_empty(row, col)
                        and (row, col) not in self._cells_removed
                    ):
                        new_playable = playable.clone()
                        new_playable.clear_cell(row, col)

                        if self._quick_uniqueness_check(
                            new_playable, row, col, playable.grid[row][col]
                        ):
                            playable = new_playable
                            self._cells_removed.add((row, col))
                            successful_removals += 1
                            break

        # Fase 3: Validación final y cálculo de dificultad exacta
        if progress_callback:
            yield progress_callback(
                iterations + 5, iterations + 10, "Calculando dificultad final..."
            )

        # Hacer una validación completa final
        final_solver = OptimizedSudokuSolver(playable)
        try:
            final_solver.solve()
            difficult_coefficient = final_solver.difficult_coefficient
        except:
            # Si falla la validación final, usar el coeficiente aproximado
            pass

        # Determinar nivel de dificultad
        difficult_level = self._calculate_difficulty_level(difficult_coefficient)

        # Crear juego final
        self.final_game = SudokuGame(
            playable, solution, difficult_level, difficult_coefficient
        )

        if progress_callback:
            yield progress_callback(
                iterations + 10,
                iterations + 10,
                f"Completado: {difficult_level.name} (coef: {difficult_coefficient:.2f})",
            )

    def _calculate_difficulty_level(self, coefficient: float) -> DifficultLevel:
        """Calcula el nivel de dificultad basado en el coeficiente"""
        if coefficient < DifficultLevel.VERY_EASY.value:
            return DifficultLevel.VERY_EASY
        elif coefficient < DifficultLevel.EASY.value:
            return DifficultLevel.EASY
        elif coefficient < DifficultLevel.MEDIUM.value:
            return DifficultLevel.MEDIUM
        elif coefficient < DifficultLevel.HARD.value:
            return DifficultLevel.HARD
        elif coefficient < DifficultLevel.VERY_HARD.value:
            return DifficultLevel.VERY_HARD
        else:
            return DifficultLevel.MASTER

    @staticmethod
    def generate_puzzle(iterations: int = 70) -> SudokuGame:
        """
        Método estático para compatibilidad con la API original
        """
        generator = OptimizedSudokuGameGenerator()
        # Ejecutar generación sin callback de progreso
        for _ in generator.generate_puzzle_with_progress(iterations, None):
            pass
        return generator.get_final_game()
