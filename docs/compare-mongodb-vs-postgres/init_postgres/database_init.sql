CREATE TABLE IF NOT EXISTS rating (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL,
  film_id uuid NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  score smallint CHECK (
    score BETWEEN 1
    AND 10
  )
);
