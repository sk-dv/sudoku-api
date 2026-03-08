# Monetización y Tiers

## Filosofía

Free tiene que ser suficientemente bueno para crear hábito, pero el techo tiene que doler justo cuando el jugador ya está enganchado. El upgrade debe sentirse como alivio, no como castigo.

## Acceso por tier

Con 7 niveles, el corte es **5 free / 2 premium (71% / 29%)**:

| Nivel       | Free | Premium |
|-------------|------|---------|
| BEGINNER    | ✓    |         |
| EASY        | ✓    |         |
| MEDIUM      | ✓    |         |
| HARD        | ✓    |         |
| EXPERT      | ✓    |         |
| MASTER      |      | ✓       |
| GRANDMASTER |      | ✓       |

El jugador llega a EXPERT sintiéndose capaz, golpea el muro de MASTER, y en ese punto ya está invertido. Ese es el momento de conversión óptimo.

## Daily puzzle

- Selección determinística por fecha (sin asignación manual en BD):
  el puzzle del día se deriva de `DATE_PART('doy', CURRENT_DATE) % total_puzzles`.
- **Free:** daily de BEGINNER a EXPERT
- **Premium:** daily de todos los niveles, incluyendo MASTER y GRANDMASTER

## Pricing sugerido

- **Free:** puzzles ilimitados BEGINNER–EXPERT + daily limitado
- **Pro (~$2-4 USD/mes):** todos los niveles, daily completo, estadísticas personales (racha, tiempo promedio)
- Precio calibrado a poder adquisitivo MX (~$40-80 MXN/mes)

## Retención

- Daily crea hábito → más tiempo en app → mayor conversión orgánica
- Racha diaria como mecánica de retención (perder la racha duele)
- El GRANDMASTER como aspiracional: pocos lo completan, todos quieren intentarlo
