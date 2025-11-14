import enum


class DifficultLevel(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4
    MASTER = 5

    @property
    def display_name_es(self) -> str:
        return {
            self.EASY: "Fácil",
            self.MEDIUM: "Medio",
            self.HARD: "Difícil",
            self.EXPERT: "Experto",
            self.MASTER: "Maestro",
        }[self]

    @classmethod
    def from_string(cls, value: str) -> 'DifficultLevel':
        if not value:
            raise ValueError("El nivel de dificultad no puede estar vacío")

        normalized = value.upper().strip()

        try:
            return cls[normalized]
        except KeyError:
            pass

        spanish_map = {
            "FACIL": cls.EASY,
            "FÁCIL": cls.EASY,
            "MEDIO": cls.MEDIUM,
            "DIFICIL": cls.HARD,
            "DIFÍCIL": cls.HARD,
            "EXPERTO": cls.EXPERT,
            "MAESTRO": cls.MASTER,
        }

        if normalized in spanish_map:
            return spanish_map[normalized]

        valid = [l.name for l in cls] + list(spanish_map.keys())
        raise ValueError(f"Nivel inválido: '{value}'. Válidos: {', '.join(valid)}")

    @classmethod
    def from_coefficient(cls, coefficient: float) -> 'DifficultLevel':
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
    def get_default(cls) -> 'DifficultLevel':
        return cls.MEDIUM

    def __str__(self) -> str:
        return self.name
