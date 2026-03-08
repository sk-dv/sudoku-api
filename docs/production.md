# Estrategia de Producción

## Arquitectura objetivo

```
Cliente → Cloudflare (CDN/WAF) → Railway (API + Gunicorn + PostgreSQL)
```

## 1. Pre-generación de puzzles

La generación toma 2-4 segundos por puzzle. Crear `scripts/populate.py` y correrlo desde local apuntando al `DATABASE_URL` de Railway — no consumir recursos del servidor para esto.

```python
for level in DifficultyLevel:
    for _ in range(50):
        game = OptimizedSudokuGameGenerator.generate_puzzle(target_level=level)
        db.save_puzzle(game)
```

## Checklist de lanzamiento

1. Poblar BD con al menos 50 puzzles por nivel
2. Verificar healthcheck `/api/health`

## Costo estimado mensual

| Servicio   | Componente       | Costo        |
| ---------- | ---------------- | ------------ |
| Railway    | API + PostgreSQL | $5/mes + uso |
| Cloudflare | DNS + CDN        | $0           |
| **Total**  |                  | **~$5/mes**  |
