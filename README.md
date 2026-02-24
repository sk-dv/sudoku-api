# Sudoku Champions API

API REST para generar, validar y resolver tableros de Sudoku con múltiples niveles de dificultad. Documentación interactiva con Swagger UI.

## Requisitos

- Python 3.9+
- PostgreSQL
- Poetry

## Instalación

```bash
git clone <tu-repo>
cd sudoku-api
poetry install
poetry run python app.py
```

El servidor inicia en `http://localhost:8000`. Swagger UI disponible en `/api/docs`.

## Endpoints

| Método | Ruta             | Descripción                              |
| ------ | ---------------- | ---------------------------------------- |
| GET    | `/api/health`    | Health check                             |
| GET    | `/api/game`      | Obtener puzzle por dificultad            |
| GET    | `/api/daily`     | Puzzle del día por dificultad            |
| GET    | `/api/stats`     | Estadísticas de puzzles en BD            |
| POST   | `/api/validate`  | Validar un tablero completo              |
| POST   | `/api/solve`     | Resolver un tablero parcial              |

### GET `/api/game?difficulty=MEDIUM`

Retorna un puzzle aleatorio de la BD según dificultad.

**Parámetros:** `difficulty` (opcional): EASY | MEDIUM | HARD | EXPERT | MASTER. Default: MEDIUM.

### POST `/api/validate`

```json
{ "grid": [[1,2,3,4,5,6,7,8,9], ...] }
```

### POST `/api/solve`

```json
{ "grid": [[1,2,0,4,5,6,7,8,9], ...] }
```

Celdas vacías representadas con `0`.

## Niveles de Dificultad

| Input API | Nombre en BD | Coeficiente   |
| --------- | ------------ | ------------- |
| EASY      | VERY_EASY    | < 3.5         |
| MEDIUM    | EASY         | 3.5 - 5.5     |
| HARD      | HARD         | 5.5 - 7.0     |
| EXPERT    | VERY_HARD    | 7.0 - 8.5     |
| MASTER    | MASTER       | >= 8.5        |

## Estructura del Proyecto

```
sudoku-api/
├── app.py                          # Entry point, factory Flask + Swagger
├── pyproject.toml                  # Dependencias (Poetry)
├── railway.json                    # Config de despliegue Railway
├── migrations/
│   ├── 001_initial.sql             # Schema inicial (puzzles)
│   └── add_date_assigned.sql       # Columna para puzzle diario
├── sudoku_api/
│   ├── __init__.py
│   ├── config.py                   # Configuración Flask
│   ├── enums.py                    # DifficultyLevel enum
│   ├── api_models.py               # Modelos Swagger
│   ├── routes.py                   # Registro de rutas
│   ├── database.py                 # Interfaz PostgreSQL
│   ├── sudoku_board.py             # Generación de tablero completo
│   ├── sudoku_solver.py            # Solver con heurística MRV
│   ├── sudoku_game.py              # Generador de puzzles jugables
│   ├── improved_difficulty.py      # Cálculo de coeficiente de dificultad
│   ├── validator.py                # Validación de tableros
│   └── resources/
│       ├── __init__.py
│       ├── health.py
│       ├── game.py
│       ├── daily.py
│       ├── validate.py
│       ├── solve.py
│       └── stats.py
└── tests/
    ├── test_api.py
    └── test_validator.py
```

## Testing

```bash
poetry run pytest tests/
```

## Variables de Entorno

```bash
DATABASE_URL=postgresql://...    # Conexión PostgreSQL (requerida)
PORT=8000                        # Puerto del servidor
FLASK_ENV=production             # development | production
```

## Despliegue

Configurado para Railway con Gunicorn + Gevent. Push a `main` despliega automáticamente.
