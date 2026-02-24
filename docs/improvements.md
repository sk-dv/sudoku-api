# Análisis de Mejoras

## 1. `DailyPuzzleResource` no implementa lógica de puzzle diario

`daily.py` es literalmente:

```python
class DailyPuzzleResource(GameResource):
    pass
```

No filtra por `date_assigned`. Retorna un puzzle aleatorio igual que `/api/game`. La migración `add_date_assigned.sql` y el índice existen pero no se usan.

## 2. Bare `except` en el generador

En `sudoku_game.py:63-65`:

```python
try:
    solver.solve()
    playable = new_playable
    successful_removals += 1
except:
    continue
```

El `except` sin tipo captura todo, incluyendo `KeyboardInterrupt` y `SystemExit`. Debería capturar `Exception` como mínimo.

## 3. Sin manejo de BD ausente

`database.py` hace `os.environ.get("DATABASE_URL")` sin fallback. Si `DATABASE_URL` no está definida, `psycopg2.connect(None)` lanza un error críptico. No hay modo de desarrollo sin BD.

## 4. Conexión a BD sin pool

Cada request crea una nueva conexión con `psycopg2.connect()`. En producción con tráfico concurrente, esto agota conexiones rápidamente. Se necesita connection pooling.

## 5. `ORDER BY RANDOM()` no escala

`find_puzzle` usa `ORDER BY RANDOM() LIMIT 1`, que hace full table scan. Con miles de puzzles por nivel, el rendimiento se degrada.

## 6. Coeficiente legacy sin uso

El solver calcula dos coeficientes: `difficult_coefficient` (legacy) e `improved_coefficient`. Solo se usa `improved_coefficient` en `sudoku_game.py`. El legacy se mantiene por "compatibilidad" pero no se consume en ningún endpoint.

## 7. Sin validación de input en endpoints

`/api/validate` y `/api/solve` no validan que el grid sea una matriz 9x9 con valores 0-9. Un grid malformado genera errores internos en lugar de un 400 descriptivo.

## 8. CORS abierto

`CORS(app)` sin restricción acepta requests desde cualquier origen. Adecuado para desarrollo, riesgo en producción.

## 9. Sin logging estructurado

No hay logging. Los errores se capturan y se devuelven como strings al cliente (`str(e)`), lo que puede filtrar información interna y dificulta el debugging en producción.