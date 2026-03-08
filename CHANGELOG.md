# Changelog

---

## [3.1.0] - 2026-03-08

### Added
- `sudoku_api/monitoring.py`: inicialización de Sentry con `LoggingIntegration` — captura `logger.exception()` como errores, ignora niveles menores a WARNING.
- `sudoku_api/middleware.py`: security headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`) vía `after_request`.
- `sudoku_api/auth.py`: decorator `require_api_key` — protege endpoints con header `X-API-Key`. Sin-op si `API_KEY` no está definida.

### Changed
- `app.py` refactorizado como factory delgado: delega Sentry, hooks y rutas a sus módulos.
- `/api/solve` y `/api/validate` requieren `X-API-Key` cuando `API_KEY` está definida en entorno.

---

## [3.0.0] - 2026-03-08

### Changed
- `DifficultyLevel` expandido de 5 a 7 niveles: BEGINNER, EASY, MEDIUM, HARD, EXPERT, MASTER, GRANDMASTER con distribución uniforme de coeficiente (intervalos de ~1.3).
- `from_db_name` y `db_name` eliminados: el nombre del enum es ahora idéntico al valor en BD, sin mapeo intermedio.
- `from_string` simplificado usando `cls[normalized]` — acepta cualquier nivel por nombre.
- `from_coefficient` actualizado con los nuevos umbrales (2.3 / 3.6 / 4.9 / 6.2 / 7.5 / 8.8).
- `improved_difficulty.py`: `empty_factor` ahora escala linealmente de 25 celdas vacías (1.0) a 64 (10.0). Pesos ajustados a `0.6 / 0.25 / 0.15` para mayor dispersión entre niveles.
- `OptimizedSudokuGameGenerator.generate_puzzle` acepta `target_level`: mapea el nivel a un rango de iteraciones y reintenta hasta 3 veces si el coeficiente resultante no coincide.
- `/api/daily` ahora selecciona el puzzle de forma determinística por `day_of_year % total`: mismo puzzle para todos los usuarios en el mismo día, sin asignación manual. Acepta `?difficulty=` para elegir nivel.

### Added
- `docs/monetization.md`: arquitectura de tiers y estrategia de monetización.

### Removed
- Columna `hints_coordinates` de la tabla `puzzles` (siempre era NULL; las coordenadas se calculan en runtime).
- Columna `date_assigned` e índice `idx_date_assigned` de la tabla `puzzles` (reemplazado por selección determinística).
- `docs/levels.md` (implementado en su totalidad).

### Security
- CORS restringido vía variable de entorno `CORS_ORIGINS` (CSV). Sin la variable, cae en `*` para desarrollo.
- Flask actualizado a `^3.1.0` para parchear GHSA-4grg-w6v8-c28g.
- Werkzeug actualizado a `^3.1.6` para parchear GHSA-hgf8-39gv-g3f2 y su bypass.

### Fixed
- `validate_grid_format` extraída a `validator.py` y reutilizada en `/api/validate` y `/api/solve`.
- `ORDER BY RANDOM()` reemplazado por `COUNT` + `OFFSET` aleatorio.
- Coeficiente legacy eliminado de `OptimizedSudokuSolver`.
- `DATABASE_URL` ausente ahora lanza `EnvironmentError` con mensaje claro.
- Conexión a BD reemplazada por `ThreadedConnectionPool` (min=1, max=10).

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
