from functools import lru_cache
from sudoku_api.improved_difficulty import FastDifficultyCalculator


class OptimizedSudokuSolver:
    def __init__(self, sudoku_board):
        self.sudoku_board = sudoku_board
        self._num_empty_cells = len(sudoku_board.get_empty_cells())
        self.difficult_coefficient = 0
        self.improved_coefficient = 0  # ← Agregar esta línea
        self._solution_count = 0
        self._max_solutions = 2  # Solo necesitamos saber si hay más de una

    def solve(self):
        """Resuelve el sudoku y retorna la solución"""
        solutions = []
        self.solve_traversal(self.sudoku_board, solutions)

        if len(solutions) > 1:
            raise Exception("Sudoku has more than one solution")
        elif len(solutions) == 0:
            raise Exception("Sudoku has no solution")

        # Coeficiente legacy (mantener compatibilidad)
        self.difficult_coefficient /= max(self._num_empty_cells, 1)
        
        # Nuevo coeficiente mejorado (rápido)
        difficulty_calc = FastDifficultyCalculator(self.sudoku_board)
        self.improved_coefficient = difficulty_calc.calculate_improved_coefficient()
        
        return solutions[0]

    def solve_traversal(self, sudoku_board, solutions):
        """Traversal optimizado con poda temprana"""
        # Si ya encontramos suficientes soluciones, parar
        if len(solutions) >= self._max_solutions:
            return

        cells_to_solve = sudoku_board.get_empty_cells()

        # Si no hay celdas vacías, encontramos una solución
        if not cells_to_solve:
            if sudoku_board not in solutions:
                solutions.append(sudoku_board)
                self._solution_count += 1
            return

        # Ordenar celdas por número de opciones disponibles (MRV heuristic)
        cells_with_options = []
        for row_num, column_num in cells_to_solve:
            available = sudoku_board.get_available_numbers(row_num, column_num)

            # Poda temprana: si una celda no tiene opciones, este camino no tiene solución
            if not available:
                return

            cells_with_options.append((len(available), row_num, column_num, available))

        # Ordenar por número de opciones (menos opciones primero)
        cells_with_options.sort(key=lambda x: x[0])

        # Tomar la celda con menos opciones
        _, row_num, column_num, available_numbers = cells_with_options[0]

        # Actualizar coeficiente de dificultad
        self.difficult_coefficient += len(available_numbers)

        # Probar cada número disponible
        for number in available_numbers:
            # Poda: si ya tenemos suficientes soluciones, parar
            if len(solutions) >= self._max_solutions:
                return

            sudoku_copy = sudoku_board.clone()
            sudoku_copy.assign(row_num, column_num, number)

            # Verificación rápida de consistencia antes de continuar
            if self._is_consistent(sudoku_copy):
                self.solve_traversal(sudoku_copy, solutions)

    def _is_consistent(self, board):
        """
        Verificación rápida de consistencia
        Retorna False si detecta una contradicción obvia
        """
        # Verificar si alguna celda vacía no tiene opciones disponibles
        empty_cells = board.get_empty_cells()

        # Solo verificar las primeras celdas para rapidez
        for row, col in empty_cells[: min(3, len(empty_cells))]:
            if len(board.get_available_numbers(row, col)) == 0:
                return False

        return True

    def has_unique_solution(self):
        """
        Método rápido para verificar si tiene solución única
        sin calcular el coeficiente de dificultad completo
        """
        solutions = []
        self._max_solutions = 2  # Solo necesitamos encontrar máximo 2
        self.solve_traversal(self.sudoku_board, solutions)
        return len(solutions) == 1
