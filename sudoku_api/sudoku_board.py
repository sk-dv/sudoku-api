import random
import copy


class SudokuBoard:

    def __init__(self, grid=None):
        self._grid = grid if grid else [[0] * 9 for _ in range(9)]

    def build(self):
        attempts, row_num = 0, 0
        while row_num < 9:
            while not self._build_new_row(row_num):
                self._grid[row_num] = [0] * 9
                attempts += 1

                if attempts > 50:
                    self._grid = [[0 for _ in range(9)] for _ in range(9)]
                    attempts, row_num = 0, 0
                    continue

            row_num += 1

    def _build_new_row(self, row_num):
        for column_num in range(9):
            available_numbers = self.get_available_numbers(row_num, column_num)
            if not available_numbers:
                return False
            number = random.choice(list(available_numbers))
            self._grid[row_num][column_num] = number
        return True

    def get_available_numbers(self, row_num, column_num):
        row_occupied_numbers = {self._grid[row_num][j] for j in range(9)}
        column_occupied_numbers = {self._grid[i][column_num] for i in range(9)}
        sub__grid_low_row = row_num - row_num % 3
        sub__grid_low_column = column_num - column_num % 3
        sub__grid_occupied_numbers = {self._grid[i][j] for i in range(sub__grid_low_row, sub__grid_low_row + 3)
                                     for j in range(sub__grid_low_column, sub__grid_low_column + 3)}
        occupied_numbers = row_occupied_numbers | column_occupied_numbers | sub__grid_occupied_numbers
        return {1, 2, 3, 4, 5, 6, 7, 8, 9} - occupied_numbers

    def get_empty_cells(self):
        return [(row_num, column_num) for row_num in range(9) for column_num in range(9) if not self._grid[row_num][column_num]]

    def assign(self, row_num, column_num, number):
        assert number in self.get_available_numbers(row_num, column_num)
        self._grid[row_num][column_num] = number

    # Returns if each row fulfills the criterion of having only one element from 1 to 9
    def _check_rows(self):
        for row in self._grid:
            if len(set(row) - {0}) != 9:
                return False
        return True

    # Returns if each column fulfills the criterion of having only one element from 1 to 9
    def _check_columns(self):
        for icolumn in range(9):
            column = [row[icolumn] for row in self._grid]
            if len(set(column) - {0}) != 9:
                return False
        return True

    # Returns if each sub _grid fulfills the criterion of having only one element from 1 to 9
    def _check_sub_grids(self):
        for irow in range(0, 9, 3):
            for icolumn in range(0, 9, 3):
                sub_grid = [self._grid[i][j] for i in range(irow, irow + 3) for j in range(icolumn, icolumn + 3)]
                if len(set(sub_grid) - {0}) != 9:
                    return False
        return True

    def clear_cell(self, row_num, column_num):
        self._grid[row_num][column_num] = 0

    def is_cell_empty(self, row_num, column_num):
        return self._grid[row_num][column_num] == 0

    def clone(self):
        new_sudoku_grid = copy.deepcopy(self._grid)
        return SudokuBoard(new_sudoku_grid)

    # Returns if the sudoku matrix is valid or not.
    @property
    def is_valid(self):
        return self._check_rows() and self._check_columns() and self._check_sub_grids()

    @property
    def grid(self):
        return self._grid

    def __eq__(self, other):
        return self._grid == other.grid

    def __str__(self):
        return "\n".join([str(row) for row in self._grid])
