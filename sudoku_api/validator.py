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
                sub_grid = [self.matrix[i][j] for i in range(irow, irow + 3) for j in range(icolumn, icolumn + 3)]
                if len(set(sub_grid)) != self.SUDOKU_NUMBER:
                    return False
        return True

    # Returns if the sudoku matrix is correct or not.
    @property
    def is_valid(self):
        return self._check_rows() and self._check_columns() and self._check_sub_grids()
