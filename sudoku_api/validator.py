class Validator:
    SUDOKU_NUMBER = 9

    def __init__(self, matrix):
        self.matrix = matrix

    # Returns if each row fulfills the criterion of having only one element from 1 to 9
    def _check_rows(self):
        for row in self.matrix:
            if len(set(row)) != self.SUDOKU_NUMBER:
                return False
        return True

    # Returns if each column fulfills the criterion of having only one element from 1 to 9
    def _check_columns(self):
        for icolumn in range(self.SUDOKU_NUMBER):
            column = [row[icolumn] for row in self.matrix]
            if len(set(column)) != self.SUDOKU_NUMBER:
                return False
        return True

    # Returns if each sub grid fulfills the criterion of having only one element from 1 to 9
    def _check_sub_grids(self):
        for irow in range(0, self.SUDOKU_NUMBER, 3):
            for icolumn in range(0, self.SUDOKU_NUMBER, 3):
                sub_grid = [
                    self.matrix[i][j]
                    for i in range(irow, irow + 3)
                    for j in range(icolumn, icolumn + 3)
                ]
                if len(set(sub_grid)) != self.SUDOKU_NUMBER:
                    return False
        return True

    # Returns if the sudoku matrix is correct or not.
    @property
    def is_valid(self):
        return self._check_rows() and self._check_columns() and self._check_sub_grids()


def validate_grid_format(grid):
    """Valida que el grid sea una matriz 9x9 con valores enteros 0-9.
    Retorna un mensaje de error si es inválido, None si es válido."""
    if not isinstance(grid, list) or len(grid) != 9:
        return "Invalid grid format"
    for i, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != 9:
            return f"Row {i} must have 9 elements"
        for j, cell in enumerate(row):
            if not isinstance(cell, int) or not 0 <= cell <= 9:
                return f"Invalid cell at [{i}][{j}]"
    return None
