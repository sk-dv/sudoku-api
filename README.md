# Sudoku

<br>

## Comandos

| Comando                           | Descripción                                           |
|-----------------------------------|-------------------------------------------------------|
| `poetry new <package-name>`       | Inicia un nuevo proyecto de python.                   |
| `poetry init`                     | Crea un archivo pyproject.toml interactivamente.      |
| `poetry install`                  | Instala los paquetes del pyproject.toml.              |
| `poetry add <package-name>`       | Agrega un paquete al ambiente virtual.                |
| `poetry add -D <package-name>`    | Agrega un paquete de dev al ambiente virtual.         |
| `poetry remove <package-name>`    | Quita un paquete del ambiente virtual.                |
| `poetry remove -D <package-name>` | Quita un paquete de dev del ambiente virtual.         |
| `poetry update`                   | Actualiza a la última versión estable de poetry.      |

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

<br>

## Referencias 

[Python projects with Poetry and VSCode](https://www.pythoncheatsheet.org/blog/python-projects-with-poetry-and-vscode-part-1)