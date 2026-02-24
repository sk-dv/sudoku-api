# Changelog

---

## [Unreleased]

### Security
- Flask actualizado a `^3.1.0` para parchear GHSA-4grg-w6v8-c28g: el header `Vary: Cookie` no se establecía al acceder al session con el operador `in`, lo que podía llevar a que proxies cachearan respuestas con datos de sesión de usuarios autenticados.
- Werkzeug actualizado a `^3.1.6` para parchear dos vulnerabilidades en `safe_join` (GHSA-hgf8-39gv-g3f2 y su bypass): nombres de dispositivo Windows (`CON`, `AUX`, etc.) con extensiones compuestas o espacios al final podían colgar la lectura indefinidamente en `send_from_directory`.

### Added
- `/api/daily` implementado: retorna el puzzle asignado a la fecha actual filtrando por `date_assigned`. Devuelve 404 si no hay puzzle asignado para hoy. La respuesta incluye `is_daily: true` y `date_assigned` en metadata.
- `DifficultyLevel.from_db_name` para convertir valores de BD al nombre de API consistente.
- `PuzzleDB.find_daily_puzzle(date)` para consultar puzzles por fecha.

### Fixed
- Bare `except` en `sudoku_game.py` reemplazado por `except Exception` para no suprimir `KeyboardInterrupt` y `SystemExit`.
- `DATABASE_URL` ausente ahora lanza `EnvironmentError` con mensaje claro en lugar de un error críptico de psycopg2.
- Conexión a BD reemplazada por `ThreadedConnectionPool` (min=1, max=10): una sola instancia de pool por proceso, las conexiones se reutilizan entre requests.
- `DifficultyLevel.name` ya no sobreescribe el comportamiento natural de Python. Se agregó `db_name` para encapsular el mapeo al esquema de BD. La respuesta de `/api/game` ahora refleja el mismo nivel que el cliente envió (`MEDIUM` → `MEDIUM`, no `EASY`).

---

## [2.0.0] - 2025

### Changed
- Migración completa de GraphQL (Strawberry) a REST API con Flask-RESTX.
- Documentación automática vía Swagger UI en `/api/docs`.
- Estructura del proyecto reorganizada en módulos (`resources/`, `sudoku_api/`).
- Sistema de dificultad mejorado: `improved_coefficient` reemplaza al coeficiente legacy.
- Inicialización lazy de la BD para evitar timeout en health check.

### Added
- Endpoints REST: `/api/game`, `/api/daily`, `/api/validate`, `/api/solve`, `/api/stats`, `/api/health`.
- Sistema de puzzle diario con columna `date_assigned` en BD.
- Enum `DifficultyLevel` con mapeo a niveles de BD.
- Solver optimizado con heurística MRV y poda temprana.
- Soporte de workers gevent para concurrencia en producción.

### Removed
- API GraphQL y dependencia de Strawberry.
- `requirements.txt` — reemplazado por `pyproject.toml` con Poetry.

---

## [1.0.0] - 2024

### Added
- Proyecto inicial con API GraphQL (Strawberry).
- Generador de puzzles Sudoku con verificación de solución única.
- Validador de grids con comprobación de filas, columnas y subcuadrículas.
- Integración con PostgreSQL vía psycopg2.
- Configuración de despliegue en Railway.