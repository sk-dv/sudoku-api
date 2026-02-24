# Análisis de Mejoras

## 1. Sin logging estructurado

No hay logging. Los errores se capturan y se devuelven como strings al cliente (`str(e)`), lo que puede filtrar información interna y dificulta el debugging en producción.