-- Migración: Agregar columna date_assigned para puzzles diarios
-- Fecha: 2025-10-02

ALTER TABLE puzzles ADD COLUMN IF NOT EXISTS date_assigned DATE;

-- Crear índice para búsquedas rápidas por dificultad y fecha
CREATE INDEX IF NOT EXISTS idx_date_assigned ON puzzles(difficulty, date_assigned);

-- Comentario sobre el uso
COMMENT ON COLUMN puzzles.date_assigned IS 'Fecha asignada para puzzle diario (NULL = no asignado)';
