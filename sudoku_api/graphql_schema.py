import sudoku_game
import enum
import typing
import strawberry


@strawberry.enum
class DifficultLevel(enum.Enum):
    VERY_EASY = 2
    EASY = 3
    MEDIUM = 5
    HARD = 7
    VERY_HARD = 10
    MASTER = 100


@strawberry.type
class SudokuBoard:
    is_valid: bool
    grid: typing.List[typing.List[int]]


@strawberry.type
class SudokuGame:
    playable: SudokuBoard
    solution: SudokuBoard
    difficult_level: DifficultLevel
    difficult_coefficient: float


@strawberry.type
class Query:
    @strawberry.field
    def game(self) -> SudokuGame:
        return sudoku_game.SudokuGameGenerator.generate_puzzle()


schema = strawberry.Schema(query=Query)
