# Sudoku

<br>

## Comandos

| Comando                                                                        | Descripción                                           |
|--------------------------------------------------------------------------------|-------------------------------------------------------|
| `poetry new <package-name>`                                                    | Inicia un nuevo proyecto de python.                   |
| `poetry init`                                                                  | Crea un archivo pyproject.toml interactivamente.      |
| `poetry install`                                                               | Instala los paquetes del pyproject.toml.              |
| `poetry add <package-name>`                                                    | Agrega un paquete al ambiente virtual.                |
| `poetry add -D <package-name>`                                                 | Agrega un paquete de dev al ambiente virtual.         |
| `poetry remove <package-name>`                                                 | Quita un paquete del ambiente virtual.                |
| `poetry remove -D <package-name>`                                              | Quita un paquete de dev del ambiente virtual.         |
| `poetry update`                                                                | Actualiza a la última versión estable de poetry.      |
| `poetry run python run.py`                                                     | Ejecución en ambiente local                           |
| `poetry lock`                                                                  | Bloquea las versiones de las dependencias             |
| `poetry export -f requirements.txt --output requirements.txt --without-hashes` | Configura Poetry para exportar requirements.txt

<br>

## Ambiente local en vscode

Actualizar dependencias de poetry

```
~$ poetry update
```

Iniciar ambiente virtual

```
~$ poetry shell
```

Abrir ambiente en vscode

```
~$ code .
```

Generar `requirements.txt`

```
~$ poetry export --without-hashes --format=requirements.txt > requirements.txt
```

<br>

## Ejecutar pruebas

```
~$ python3 -m unittest tests/test_validator.py
```

<br>

## GraphQL Schema

Correr servidor

```
~$ strawberry server graphql_schema:schema
```

Generar nuevo schema 

```
~$ strawberry export-schema graphql_schema:schema > ../schema.graphql
```

<br>

## Referencias 

[Strawberry GraphQL Playground | Sudoku Game Example](https://play.strawberry.rocks/?gist=701a12d9374f01fc610afdf274aa6ad4)

[Python projects with Poetry and VSCode](https://www.pythoncheatsheet.org/blog/python-projects-with-poetry-and-vscode-part-1)