# Arquitectura y Lógica del Sistema

## Flujo de Generación de Puzzles

### 1. Tablero completo (`sudoku_board.py`)

Genera un tablero 9x9 válido fila por fila con backtracking:

1. Para cada fila, intenta llenar cada celda con un número válido aleatorio
2. Si no puede completar la fila, la reinicia
3. Tras 50 fallos en una fila, reinicia todo el tablero

### 2. Eliminación de celdas (`sudoku_game.py`)

Convierte el tablero completo en un puzzle jugable:

1. Clona el tablero resuelto
2. En cada iteración (default 70, máximo 64 celdas vacías):
   - Selecciona celda aleatoria no vacía
   - La elimina y verifica solución única con el solver
   - Si tiene solución única, mantiene el cambio
   - Si no, descarta y continúa

### 3. Solver (`sudoku_solver.py`)

Backtracking con heurística MRV (Minimum Remaining Values):

- Ordena celdas vacías por cantidad de opciones disponibles (menos primero)
- Poda temprana: si una celda tiene 0 opciones, descarta la rama
- Verificación de consistencia: revisa las primeras 3 celdas vacías tras cada asignación
- Para después de encontrar 2 soluciones (suficiente para validar unicidad)

### 4. Coeficiente de dificultad (`improved_difficulty.py`)

Fórmula: `score = empty_factor * 0.5 + options_factor * 0.3 + spatial_factor * 0.2`

| Factor          | Peso | Cálculo                                              |
| --------------- | ---- | ---------------------------------------------------- |
| empty_factor    | 50%  | `(celdas_vacías / 81) * 15`, capped a 10             |
| options_factor  | 30%  | Promedio de opciones por celda + penalización por restricciones |
| spatial_factor  | 20%  | Distribución de vacías entre las 9 regiones 3x3      |

Resultado: valor entre 1.0 y 10.0.

### 5. Clasificación de niveles (`enums.py`)

El coeficiente se mapea a niveles con `from_coefficient()`:

| Coeficiente | Nivel interno | Nombre en BD/API |
| ----------- | ------------- | ----------------- |
| < 3.5       | EASY          | VERY_EASY         |
| 3.5 - 5.5   | MEDIUM        | EASY              |
| 5.5 - 7.0   | HARD          | HARD              |
| 7.0 - 8.5   | EXPERT        | VERY_HARD         |
| >= 8.5      | MASTER        | MASTER            |

## Flujo de la API

La API no genera puzzles en tiempo real. Sirve puzzles pre-generados desde PostgreSQL:

1. El cliente envía `GET /api/game?difficulty=MEDIUM`
2. `GameResource` convierte el input a `DifficultyLevel` enum
3. Obtiene `difficulty_level.name` (e.g., MEDIUM → "EASY")
4. Consulta `puzzles` con `WHERE difficulty = 'EASY' ORDER BY RANDOM() LIMIT 1`
5. Retorna el puzzle con su grid, solución, coeficiente y coordenadas de hints

## Base de Datos

```sql
CREATE TABLE puzzles (
    id SERIAL PRIMARY KEY,
    difficulty VARCHAR(20) NOT NULL,     -- VERY_EASY, EASY, HARD, VERY_HARD, MASTER
    empty_cells INTEGER NOT NULL,
    playable_grid JSON NOT NULL,
    solution_grid JSON NOT NULL,
    coefficient FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    date_assigned DATE                   -- Para puzzle diario
);
```

Índices: `(difficulty, empty_cells)` y `(difficulty, date_assigned)`.

## Despliegue actual

Railway con Gunicorn + Gevent, 1 worker, timeout 120s. Healthcheck en `/api/health`.
