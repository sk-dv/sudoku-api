CREATE TABLE IF NOT EXISTS puzzles (
    id SERIAL PRIMARY KEY,
    difficulty VARCHAR(20) NOT NULL,
    empty_cells INTEGER NOT NULL,
    playable_grid JSON NOT NULL,
    solution_grid JSON NOT NULL,
    coefficient FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_difficulty_empty ON puzzles(difficulty, empty_cells);