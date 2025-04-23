FROM python:3.9-slim

# Instalar Poetry
RUN pip install poetry

WORKDIR /app

# Copiar archivos de configuración de Poetry
COPY pyproject.toml poetry.lock* ./

# Configurar Poetry para no crear un entorno virtual dentro del contenedor
RUN poetry config virtualenvs.create false

# Instalar dependencias
RUN poetry install --no-dev

# Copiar el código de la aplicación
COPY sudoku_api/ .

ENV PORT=8080
ENV GRAPHIQL=true

CMD ["python", "server.py"]