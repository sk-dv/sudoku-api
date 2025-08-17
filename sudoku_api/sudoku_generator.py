import random
import time
from typing import List, Tuple
from sudoku_api.sudoku_board import SudokuBoard


class FastSudokuSolver:
    """Solver optimizado que solo verifica unicidad de solución"""

    def __init__(self, board: SudokuBoard):
        self.board = board
        self.solution_count = 0
        self.max_solutions = 2  # Solo necesitamos saber si hay 1 o más de 1
        self.difficulty_score = 0

    def has_unique_solution(self) -> Tuple[bool, float]:
        """
        Verifica si tiene solución única sin resolverlo completamente.
        Retorna (tiene_solucion_unica, puntuacion_dificultad)
        """
        self.solution_count = 0
        self.difficulty_score = 0
        board_copy = self.board.clone()

        self._solve_with_counting(board_copy)

        # Calcular dificultad basada en celdas vacías y ramificación
        empty_count = len(board_copy.get_empty_cells())
        difficulty = (
            self.difficulty_score / max(empty_count, 1) if empty_count > 0 else 1
        )

        return self.solution_count == 1, difficulty

    def _solve_with_counting(self, board: SudokuBoard) -> bool:
        """Cuenta soluciones hasta encontrar más de 1"""
        if self.solution_count >= self.max_solutions:
            return True

        empty_cells = board.get_empty_cells()
        if not empty_cells:
            self.solution_count += 1
            return self.solution_count >= self.max_solutions

        # Tomar la celda con menos opciones (MRV - Most Restricted Variable)
        empty_cells.sort(
            key=lambda coords: len(board.get_available_numbers(coords[0], coords[1]))
        )
        row, col = empty_cells[0]
        available = board.get_available_numbers(row, col)

        # Incrementar score de dificultad
        self.difficulty_score += len(available)

        for number in available:
            board.assign(row, col, number)
            if self._solve_with_counting(board):
                return True
            board.clear_cell(row, col)

        return False


class OptimizedSudokuGenerator:
    """Generador optimizado de puzzles de Sudoku"""

    @staticmethod
    def generate_puzzle(iterations: int = 70):
        """
        Genera puzzle optimizado manteniendo compatibilidad con la API original
        """
        start_time = time.time()

        # 1. Generar solución completa
        solution = SudokuBoard()
        solution.build()

        # 2. Estrategia de remoción inteligente
        puzzle = solution.clone()
        current_difficulty = 1.0
        successful_removals = 0

        # Lista de celdas en orden estratégico
        cell_priority = OptimizedSudokuGenerator._get_strategic_removal_order()

        for iteration in range(min(iterations, 81)):  # Máximo 81 celdas
            # Timeout de seguridad
            if time.time() - start_time > 30:
                break

            # Seleccionar celda estratégicamente si es posible
            if iteration < len(cell_priority):
                row, col = cell_priority[iteration]
            else:
                # Si se acabaron las celdas estratégicas, usar aleatorio
                filled_cells = [
                    (r, c) for r in range(9) for c in range(9) if puzzle.grid[r][c] != 0
                ]
                if not filled_cells:
                    break
                row, col = random.choice(filled_cells)

            # Si la celda ya está vacía, continuar
            if puzzle.grid[row][col] == 0:
                continue

            # Guardar valor y remover temporalmente
            original_value = puzzle.grid[row][col]
            puzzle.clear_cell(row, col)

            # Verificar si mantiene solución única con timeout
            try:
                solver = FastSudokuSolver(puzzle)
                has_unique, difficulty = solver.has_unique_solution()

                if has_unique:
                    # Aceptar remoción
                    successful_removals += 1
                    current_difficulty = difficulty
                else:
                    # Rechazar remoción, restaurar valor
                    puzzle.assign(row, col, original_value)
            except:
                # En caso de error, restaurar valor
                puzzle.assign(row, col, original_value)

        # Crear objeto compatible con la estructura original
        from sudoku_api.sudoku_game import DifficultLevel, SudokuGame

        # Clasificar dificultad
        if current_difficulty < DifficultLevel.VERY_EASY.value:
            difficult_level = DifficultLevel.VERY_EASY
        elif current_difficulty < DifficultLevel.EASY.value:
            difficult_level = DifficultLevel.EASY
        elif current_difficulty < DifficultLevel.MEDIUM.value:
            difficult_level = DifficultLevel.MEDIUM
        elif current_difficulty < DifficultLevel.HARD.value:
            difficult_level = DifficultLevel.HARD
        elif current_difficulty < DifficultLevel.VERY_HARD.value:
            difficult_level = DifficultLevel.VERY_HARD
        else:
            difficult_level = DifficultLevel.MASTER

        return SudokuGame(puzzle, solution, difficult_level, current_difficulty)

    @staticmethod
    def _get_strategic_removal_order() -> List[Tuple[int, int]]:
        """
        Orden estratégico para remover celdas:
        1. Centro (más impacto en dificultad)
        2. Celdas que afectan múltiples cajas
        3. Distribución equilibrada
        """
        cells = []

        # Centro del tablero (mayor impacto en dificultad)
        center_cells = [
            (4, 4),  # Centro absoluto
            (3, 4),
            (4, 3),
            (5, 4),
            (4, 5),  # Cruz central
            (3, 3),
            (3, 5),
            (5, 3),
            (5, 5),  # Esquinas del centro
        ]
        cells.extend(center_cells)

        # Celdas que conectan múltiples cajas (alta influencia)
        connector_cells = [
            (1, 1),
            (1, 7),
            (7, 1),
            (7, 7),  # Esquinas de cajas intermedias
            (1, 4),
            (4, 1),
            (4, 7),
            (7, 4),  # Conectores de cruz
            (2, 2),
            (2, 6),
            (6, 2),
            (6, 6),  # Esquinas de cajas externas
        ]
        cells.extend(connector_cells)

        # Resto de celdas distribuidas uniformemente
        remaining = []
        for r in range(9):
            for c in range(9):
                if (r, c) not in cells:
                    remaining.append((r, c))

        # Mezclar el resto para evitar patrones predecibles
        random.shuffle(remaining)
        cells.extend(remaining)

        return cells
