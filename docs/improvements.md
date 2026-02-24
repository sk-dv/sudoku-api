# Análisis de Mejoras

## 1. `ORDER BY RANDOM()` no escala

`find_puzzle` usa `ORDER BY RANDOM() LIMIT 1`, que hace full table scan. Con miles de puzzles por nivel, el rendimiento se degrada.

## 2. Coeficiente legacy sin uso

El solver calcula dos coeficientes: `difficult_coefficient` (legacy) e `improved_coefficient`. Solo se usa `improved_coefficient` en `sudoku_game.py`. El legacy se mantiene por "compatibilidad" pero no se consume en ningún endpoint.

## 3. Sin validación de input en endpoints

`/api/validate` y `/api/solve` no validan que el grid sea una matriz 9x9 con valores 0-9. Un grid malformado genera errores internos en lugar de un 400 descriptivo.

## 4. CORS abierto

`CORS(app)` sin restricción acepta requests desde cualquier origen. Adecuado para desarrollo, riesgo en producción.

## 5. Sin logging estructurado

No hay logging. Los errores se capturan y se devuelven como strings al cliente (`str(e)`), lo que puede filtrar información interna y dificulta el debugging en producción.