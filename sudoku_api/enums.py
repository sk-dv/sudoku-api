import enum


class DifficultyLevel(enum.Enum):
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5
    MASTER = 6
    GRANDMASTER = 7

    @classmethod
    def from_string(cls, value: str) -> 'DifficultyLevel':
        if not value:
            raise ValueError("El nivel de dificultad no puede estar vacío")

        normalized = value.strip().upper()

        try:
            return cls[normalized]
        except KeyError:
            raise ValueError(f"Nivel inválido: '{value}'")

    @classmethod
    def from_coefficient(cls, coefficient: float) -> 'DifficultyLevel':
        thresholds = [
            (2.3, cls.BEGINNER),
            (3.6, cls.EASY),
            (4.9, cls.MEDIUM),
            (6.2, cls.HARD),
            (7.5, cls.EXPERT),
            (8.8, cls.MASTER),
        ]
        for threshold, level in thresholds:
            if coefficient < threshold:
                return level
        return cls.GRANDMASTER

    @classmethod
    def get_default(cls) -> 'DifficultyLevel':
        return cls.MEDIUM

    def __str__(self) -> str:
        return self.name
