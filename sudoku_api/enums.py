import enum


class DifficultyLevel(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4
    MASTER = 5

    @property
    def name(self) -> str:
        match self:
            case DifficultyLevel.EASY:
                return "VERY_EASY"
            case DifficultyLevel.MEDIUM:
                return "EASY"
            case DifficultyLevel.HARD:
                return "HARD"
            case DifficultyLevel.EXPERT:
                return "VERY_HARD"
            case DifficultyLevel.MASTER:
                return "MASTER"

    @classmethod
    def from_string(cls, value: str) -> 'DifficultyLevel':
        if not value:
            raise ValueError("El nivel de dificultad no puede estar vacío")

        normalized = value.strip()

        match normalized:
            case "EASY":
                return cls.EASY
            case "MEDIUM":
                return cls.MEDIUM
            case "HARD":
                return cls.HARD
            case "EXPERT":
                return cls.EXPERT
            case "MASTER":
                return cls.MASTER
            case _:
                raise ValueError(f"Nivel inválido: '{value}'")

    @classmethod
    def from_coefficient(cls, coefficient: float) -> 'DifficultyLevel':
        if coefficient < 3.5:
            return cls.EASY
        elif coefficient < 5.5:
            return cls.MEDIUM
        elif coefficient < 7.0:
            return cls.HARD
        elif coefficient < 8.5:
            return cls.EXPERT
        else:
            return cls.MASTER

    @classmethod
    def get_default(cls) -> 'DifficultyLevel':
        return cls.MEDIUM

    def __str__(self) -> str:
        return self.name
