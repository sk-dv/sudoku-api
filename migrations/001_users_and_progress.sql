-- Migración 001: Usuarios, progreso y estadísticas
-- Ejecutar: railway run psql $DATABASE_URL -f migrations/001_users_and_progress.sql

CREATE TABLE IF NOT EXISTS users (
    id              VARCHAR(128) PRIMARY KEY,  -- Firebase UID
    email           VARCHAR(255),
    display_name    VARCHAR(255),
    is_premium      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS game_progress (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR(128) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    puzzle_id       INTEGER NOT NULL REFERENCES puzzles(id),
    current_state   INTEGER[][],
    time_elapsed    INTEGER DEFAULT 0,
    hints_used      INTEGER DEFAULT 0,
    completed       BOOLEAN DEFAULT FALSE,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    UNIQUE (user_id, puzzle_id)
);

CREATE TABLE IF NOT EXISTS user_stats (
    user_id         VARCHAR(128) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    games_played    INTEGER DEFAULT 0,
    games_completed INTEGER DEFAULT 0,
    best_times      JSONB DEFAULT '{}',
    current_streak  INTEGER DEFAULT 0,
    best_streak     INTEGER DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_game_progress_user_id ON game_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_game_progress_puzzle_id ON game_progress(puzzle_id);
