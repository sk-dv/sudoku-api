# Estandarización y Expansión de Niveles

## Problema actual

El coeficiente va de 1.0 a 10.0 pero los rangos están distribuidos de forma desigual:

```
VERY_EASY:  1.0 - 3.5   (rango: 2.5)
EASY:       3.5 - 5.5   (rango: 2.0)
HARD:       5.5 - 7.0   (rango: 1.5)
VERY_HARD:  7.0 - 8.5   (rango: 1.5)
MASTER:     8.5 - 10.0  (rango: 1.5)
```

Además, el naming es inconsistente: el enum interno (EASY, MEDIUM, HARD, EXPERT, MASTER) no coincide con lo que se persiste en BD (VERY_EASY, EASY, HARD, VERY_HARD, MASTER). No existe un nivel "MEDIUM" en BD.

## Propuesta: 7 niveles con distribución uniforme

Escala de 1.0 a 10.0, intervalos de ~1.3 puntos cada uno:

| Nivel       | Coeficiente   | Celdas vacías aprox. | Descripción              |
| ----------- | ------------- | -------------------- | ------------------------ |
| BEGINNER    | 1.0 - 2.3     | 25-30                | Resoluble con naked singles |
| EASY        | 2.3 - 3.6     | 30-38                | Singles + hidden singles   |
| MEDIUM      | 3.6 - 4.9     | 38-44                | Requiere pointing pairs    |
| HARD        | 4.9 - 6.2     | 44-50                | Box/line reduction         |
| EXPERT      | 6.2 - 7.5     | 50-55                | Naked/hidden subsets       |
| MASTER      | 7.5 - 8.8     | 55-60                | X-Wing, Swordfish          |
| GRANDMASTER | 8.8 - 10.0    | 60-64                | Backtracking necesario     |

## Cambios necesarios

### 1. `enums.py` — Reescribir el enum

```python
class DifficultyLevel(enum.Enum):
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5
    MASTER = 6
    GRANDMASTER = 7

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
```

Eliminar el override de `name`. Usar `self.name` natural de Python. Lo que entra en la API = lo que se guarda en BD = lo que se devuelve al cliente.

### 2. `improved_difficulty.py` — Calibrar el calculador

El calculador actual tiene un sesgo hacia el centro del rango (la mayoría de puzzles generados caen entre 4.0 y 7.0). Para poblar los extremos:

**Ajustar los pesos para mayor dispersión:**

```python
# Actual
final_score = empty_factor * 0.5 + options_factor * 0.3 + spatial_factor * 0.2

# Propuesto: dar más peso a celdas vacías para dispersar
final_score = empty_factor * 0.6 + options_factor * 0.25 + spatial_factor * 0.15
```

**Ajustar `empty_factor` para que cubra el rango completo:**

```python
# Actual: (total_empty / 81) * 15 → con 30 vacías = 5.5, con 60 = 11.1 (capped a 10)
# Propuesto: escalar linealmente de 25 vacías (1.0) a 64 vacías (10.0)
empty_factor = max(1.0, min(10.0, (self.total_empty - 25) / 39 * 9 + 1))
```

### 3. `sudoku_game.py` — Generar por nivel objetivo

Actualmente el generador no recibe un nivel objetivo. Genera con iteraciones fijas y clasifica después. Para poblar todos los niveles:

```python
@staticmethod
def generate_puzzle(target_level: DifficultyLevel) -> SudokuGame:
    # Mapear nivel a rango de iteraciones
    iteration_ranges = {
        DifficultyLevel.BEGINNER: (15, 30),
        DifficultyLevel.EASY: (30, 45),
        DifficultyLevel.MEDIUM: (45, 60),
        DifficultyLevel.HARD: (60, 80),
        DifficultyLevel.EXPERT: (80, 110),
        DifficultyLevel.MASTER: (110, 150),
        DifficultyLevel.GRANDMASTER: (150, 200),
    }
    min_iter, max_iter = iteration_ranges[target_level]
    iterations = random.randint(min_iter, max_iter)
    # ... resto de la generación
```

Después de generar, validar que el coeficiente resultante cae dentro del rango esperado. Si no, descartar y regenerar (máximo 3 intentos).

### 4. `database.py` — Sin cambios de schema

La columna `difficulty VARCHAR(20)` ya soporta los nuevos nombres. Solo se necesita:

- Migración de datos existentes para mapear los nombres viejos a los nuevos
- Script de repoblación para generar puzzles con los niveles faltantes

### 5. Migración de datos

```sql
UPDATE puzzles SET difficulty = 'BEGINNER' WHERE difficulty = 'VERY_EASY' AND coefficient < 2.3;
UPDATE puzzles SET difficulty = 'EASY' WHERE difficulty IN ('VERY_EASY', 'EASY') AND coefficient >= 2.3 AND coefficient < 3.6;
UPDATE puzzles SET difficulty = 'MEDIUM' WHERE difficulty = 'EASY' AND coefficient >= 3.6 AND coefficient < 4.9;
UPDATE puzzles SET difficulty = 'HARD' WHERE difficulty = 'HARD' AND coefficient >= 4.9 AND coefficient < 6.2;
UPDATE puzzles SET difficulty = 'EXPERT' WHERE difficulty IN ('HARD', 'VERY_HARD') AND coefficient >= 6.2 AND coefficient < 7.5;
UPDATE puzzles SET difficulty = 'MASTER' WHERE difficulty IN ('VERY_HARD', 'MASTER') AND coefficient >= 7.5 AND coefficient < 8.8;
UPDATE puzzles SET difficulty = 'GRANDMASTER' WHERE difficulty = 'MASTER' AND coefficient >= 8.8;
```

### 6. Orden de implementación

1. Reescribir `enums.py` con los 7 niveles
2. Ajustar `improved_difficulty.py` para dispersión
3. Modificar `sudoku_game.py` para aceptar nivel objetivo
4. Ejecutar migración SQL de datos existentes
5. Correr script de generación para poblar niveles faltantes
6. Actualizar tests
