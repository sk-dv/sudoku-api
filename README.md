# Sudoku API REST

API REST para generar, validar y resolver tableros de Sudoku con diferentes niveles de dificultad.

## 🚀 Características

- **Generación de juegos**: Crea tableros de Sudoku con dificultad personalizable
- **Validación**: Verifica si un tablero de Sudoku es válido
- **Resolución**: Resuelve tableros parcialmente completados
- **Múltiples niveles**: VERY_EASY, EASY, MEDIUM, HARD, VERY_HARD, MASTER

## 📋 Requisitos

- Python 3.9+
- Poetry (recomendado para desarrollo)

## 🛠️ Instalación

### Con Poetry (recomendado)

```bash
# Clonar repositorio
git clone <tu-repo>
cd sudoku-api

# Instalar dependencias
poetry install

# Activar ambiente virtual
poetry shell

# Ejecutar servidor
poetry run python app.py
```

### Con pip

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python app.py
```

## 🔗 Endpoints

### Health Check

```http
GET /
```

**Respuesta:**

```json
{
  "status": "ok",
  "service": "sudoku-api",
  "version": "1.0.0"
}
```

### Generar Juego

```http
GET /api/game?iterations=70
```

**Parámetros:**

- `iterations` (opcional): Número de iteraciones (10-200, default: 70)

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "playable": {
      "grid": [[1,2,3,...], ...],
      "is_valid": false
    },
    "solution": {
      "grid": [[1,2,3,...], ...],
      "is_valid": true
    },
    "difficulty": {
      "level": "MEDIUM",
      "coefficient": 4.25
    },
    "metadata": {
      "iterations_used": 70,
      "empty_cells": 45
    }
  }
}
```

### Validar Tablero

```http
POST /api/validate
Content-Type: application/json

{
  "grid": [[1,2,3,4,5,6,7,8,9], ...]
}
```

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "grid": [[1,2,3,...], ...],
    "validation_details": {
      "total_cells": 81,
      "filled_cells": 81,
      "empty_cells": 0
    }
  }
}
```

### Resolver Tablero

```http
POST /api/solve
Content-Type: application/json

{
  "grid": [[1,2,0,4,5,6,7,8,9], ...]  // 0 = celda vacía
}
```

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "original_grid": [[1,2,0,...], ...],
    "solved_grid": [[1,2,3,...], ...],
    "difficulty_coefficient": 3.45,
    "steps_taken": "Solved successfully"
  }
}
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
poetry run python -m unittest tests/test_api.py

# O con pytest (si lo instalas)
poetry add --group dev pytest
poetry run pytest tests/
```

## 🚀 Despliegue

### Railway (Recomendado)

1. Conecta tu repositorio a [Railway](https://railway.app)
2. Railway detectará automáticamente el proyecto Python
3. Se desplegará automáticamente

### Variables de entorno

```bash
PORT=8000                    # Puerto del servidor
FLASK_ENV=production        # Ambiente (development/production)
```

## 📁 Estructura del Proyecto

```
sudoku-api/
├── app.py                  # Aplicación Flask principal
├── requirements.txt        # Dependencias para producción
├── pyproject.toml         # Configuración Poetry
├── sudoku_api/
│   ├── __init__.py
│   ├── sudoku_board.py    # Lógica del tablero
│   ├── sudoku_game.py     # Generación de juegos
│   ├── sudoku_solver.py   # Algoritmo de resolución
│   └── validator.py       # Validación de tableros
└── tests/
    ├── test_api.py        # Tests de la API REST
    └── test_validator.py  # Tests del validador
```

## 📚 Niveles de Dificultad

| Nivel     | Coeficiente | Descripción                          |
| --------- | ----------- | ------------------------------------ |
| VERY_EASY | < 2         | Muy fácil, pocas opciones por celda  |
| EASY      | 2-3         | Fácil, suitable para principiantes   |
| MEDIUM    | 3-5         | Intermedio, requiere algo de lógica  |
| HARD      | 5-7         | Difícil, requiere técnicas avanzadas |
| VERY_HARD | 7-10        | Muy difícil, para expertos           |
| MASTER    | 10+         | Maestro, extremadamente desafiante   |

## 🔄 Comandos útiles

```bash
# Desarrollo
poetry run python app.py

# Testing
poetry run python -m unittest tests/test_api.py

# Generar requirements.txt
Instalar los siguientes paquetes en el ambiente: 
pip install poetry-plugin-export python-inspector

poetry export --without-hashes --format=requirements.txt > requirements.txt

# Formatear código
poetry run black .

# Levantar ambiente 
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install xyz
```
