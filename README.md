# Sudoku API REST

API REST para generar, validar y resolver tableros de Sudoku con diferentes niveles de dificultad. Incluye documentación interactiva con Swagger UI.

## 🚀 Características

- **Generación de juegos**: Crea tableros de Sudoku con dificultad personalizable
- **Puzzle diario**: Sistema de puzzle del día por nivel de dificultad
- **Validación**: Verifica si un tablero de Sudoku es válido
- **Resolución**: Resuelve tableros parcialmente completados
- **Múltiples niveles**: EASY, MEDIUM, HARD, EXPERT, MASTER
- **Caché de puzzles**: Base de datos PostgreSQL con puzzles pre-generados
- **Documentación Swagger**: Interfaz interactiva en `/api/docs`

## 📋 Requisitos

- Python 3.9+
- PostgreSQL (para producción)
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

## 📖 Documentación

Accede a la documentación interactiva Swagger UI en:

```
https://tu-app.railway.app/api/docs
```

## 🔗 Endpoints Principales

### 📊 GET `/api/boards`

Obtiene resumen de tableros disponibles por dificultad.

### 📅 GET `/api/daily?difficulty=MEDIUM`

Obtiene el puzzle del día (un puzzle único por día y dificultad).

**Parámetros:**

- `difficulty` (opcional): EASY | MEDIUM | HARD | EXPERT | MASTER

### 🎮 GET `/api/game?iterations=70&difficulty=MEDIUM`

Genera o recupera un puzzle de Sudoku (usa caché de BD si existe).

**Parámetros:**

- `iterations` (opcional): 10-200 (default: 70)
- `difficulty` (opcional): EASY | MEDIUM | HARD | EXPERT | MASTER

### 📈 GET `/api/stats`

Obtiene estadísticas de puzzles disponibles.

### ✅ POST `/api/validate`

Valida un tablero de Sudoku.

**Body:**

```json
{
  "grid": [[1,2,3,4,5,6,7,8,9], ...]
}
```

### 🧩 POST `/api/solve`

Resuelve un tablero parcialmente completado.

**Body:**

```json
{
  "grid": [[1,2,0,4,5,6,7,8,9], ...]  // 0 = celda vacía
}
```

> **Nota**: Para ver ejemplos de respuesta y probar los endpoints, visita `/api/docs`

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
PORT=8000                         # Puerto del servidor
FLASK_ENV=production              # Ambiente (development/production)
DATABASE_URL=postgresql://...     # URL de PostgreSQL (Railway lo configura automáticamente)
```

## 📁 Estructura del Proyecto

```
sudoku-api/
├── app.py                  # Aplicación Flask principal con Swagger
├── requirements.txt        # Dependencias para producción
├── pyproject.toml         # Configuración Poetry
├── migrations/            # Migraciones de base de datos
│   └── add_date_assigned.sql
├── sudoku_api/
│   ├── __init__.py
│   ├── database.py        # Conexión PostgreSQL y queries
│   ├── sudoku_board.py    # Lógica del tablero
│   ├── sudoku_game.py     # Generación de juegos
│   ├── sudoku_solver.py   # Algoritmo de resolución
│   └── validator.py       # Validación de tableros
└── tests/
    ├── test_api.py        # Tests de la API REST
    └── test_validator.py  # Tests del validador
```

## 📚 Niveles de Dificultad

| Nivel  | Descripción                          |
| ------ | ------------------------------------ |
| EASY   | Fácil, suitable para principiantes   |
| MEDIUM | Intermedio, requiere algo de lógica  |
| HARD   | Difícil, requiere técnicas avanzadas |
| EXPERT | Muy difícil, para expertos           |
| MASTER | Maestro, extremadamente desafiante   |

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
