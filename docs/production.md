# Estrategia de Producción

## Arquitectura objetivo

```
Cliente → Cloudflare (CDN/WAF) → Railway (API + Gunicorn) → Supabase (PostgreSQL)
```

## 1. Base de datos: migrar de Railway PostgreSQL a Supabase

**Por qué:** Railway cobra por hora de uso de BD (~$5-7/mes mínimo). Supabase ofrece PostgreSQL con 500MB gratis y connection pooling integrado (PgBouncer).

**Cambios:**
- Actualizar `DATABASE_URL` en Railway con la connection string de Supabase (modo `transaction` para pooling)
- En `database.py`, agregar `sslmode=require` al connect
- Ejecutar migraciones en Supabase

**Resultado:** $0/mes en BD mientras el volumen sea bajo. Connection pooling resuelve el problema de conexiones por request.

## 2. Seguridad

### API Key para endpoints de escritura

Proteger `/api/solve` y `/api/validate` con una API key simple vía header:

```python
# middleware o decorator
API_KEY = os.environ.get("API_KEY")

def require_api_key(f):
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if API_KEY and key != API_KEY:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated
```

Los endpoints GET (`/game`, `/daily`, `/stats`) pueden mantenerse públicos.

### Rate limiting

Agregar `flask-limiter` con almacenamiento en memoria (suficiente para un worker):

```python
limiter = Limiter(app, default_limits=["100 per minute"])

# Endpoints de lectura: 100/min
# Endpoints de escritura (solve/validate): 20/min
```

### CORS restrictivo

```python
CORS(app, origins=["https://tu-dominio.com"])
```

### Headers de seguridad

Agregar en la respuesta:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security` (Railway ya fuerza HTTPS)

## 3. Reducción de costos en Railway

### Worker configuration actual

```
gunicorn app:app --worker-class gevent --workers 1 --bind 0.0.0.0:$PORT --timeout 120
```

1 worker con gevent es correcto para el tier gratuito/bajo de Railway. No cambiar a múltiples workers salvo que haya carga real.

### Sleep mode

Railway permite `sleepApplication: true` en el plan Hobby. La API se duerme tras 10 minutos sin tráfico y despierta en ~2 segundos con el primer request. Reduce costos drásticamente si el uso es esporádico.

### Build cache

Railway usa Nixpacks que ya cachea layers. Asegurar que `poetry.lock` no cambie innecesariamente para aprovechar el cache de dependencias.

## 4. Observabilidad mínima

Agregar logging estructurado con `logging` de stdlib:

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
```

Railway captura stdout automáticamente. No se necesita servicio externo de logs en esta etapa.

## 5. Pre-generación de puzzles

El cuello de botella del sistema es la generación de puzzles (2-4 segundos cada uno). La API ya sirve desde BD, pero necesita un mecanismo para poblarla.

Crear un script `scripts/populate.py` que se ejecute manualmente o con un cron:

```python
# Generar N puzzles por nivel
for level in DifficultyLevel:
    for _ in range(50):
        game = OptimizedSudokuGameGenerator.generate_puzzle(target_level=level)
        db.save_puzzle(game)
```

Ejecutar desde local hacia Supabase. No consumir recursos de Railway para generación.

## 6. Checklist de lanzamiento

1. Crear proyecto en Supabase, ejecutar migraciones
2. Actualizar `DATABASE_URL` en Railway
3. Agregar `API_KEY` como variable de entorno en Railway
4. Configurar CORS con dominio(s) real(es)
5. Agregar rate limiting y headers de seguridad
6. Poblar BD con al menos 50 puzzles por nivel
7. Habilitar sleep mode en Railway
8. Verificar healthcheck y logs

## Costo estimado mensual

| Servicio    | Componente       | Costo          |
| ----------- | ---------------- | -------------- |
| Railway     | API (Hobby)      | $5/mes + uso   |
| Supabase    | PostgreSQL       | $0 (free tier) |
| Cloudflare  | DNS + CDN        | $0 (free tier) |
| **Total**   |                  | **~$5/mes**    |
