import sudoku_game
import typing
import strawberry


@strawberry.type
class SudokuBoard:
    is_valid: bool
    grid: typing.List[typing.List[int]]


@strawberry.type
class SudokuGame:
    playable: SudokuBoard
    solution: SudokuBoard
    difficult_level: sudoku_game.DifficultLevel
    difficult_coefficient: float


@strawberry.type
class Query:
    @strawberry.field
    def game(self) -> SudokuGame:
        return sudoku_game.SudokuGameGenerator.generate_puzzle()


schema = strawberry.Schema(query=Query)
