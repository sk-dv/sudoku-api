class SudokuSolver:
    def __init__(self, sudoku_board):
        self.sudoku_board = sudoku_board
        self._num_empty_cells = len(sudoku_board.get_empty_cells())
        self.difficult_coefficient = 0

    def solve(self):
        solutions = []
        self.solve_traversal(self.sudoku_board, solutions)

        if len(solutions) > 1:
            raise Exception("Sudoku has more than one solution")
        self.difficult_coefficient /= self._num_empty_cells
        return solutions[0]

    def solve_traversal(self, sudoku_board, solutions):
        cells_to_solve = sudoku_board.get_empty_cells()
        if not cells_to_solve:
            if sudoku_board not in solutions:
                solutions.append(sudoku_board)
            return
        cells_to_solve.sort(
            key=lambda coords: len(
                sudoku_board.get_available_numbers(coords[0], coords[1])
            )
        )

        row_num, column_num = cells_to_solve.pop(0)
        available_numbers = sudoku_board.get_available_numbers(row_num, column_num)

        self.difficult_coefficient += len(available_numbers)

        for number in available_numbers:
            sudoku_copy = sudoku_board.clone()
            sudoku_copy.assign(row_num, column_num, number)
            self.solve_traversal(sudoku_copy, solutions)
