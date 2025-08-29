-- Deduplication and Retrieval Optimization
ALTER TABLE session_items
  ADD COLUMN IF NOT EXISTS content_hash bytea,
  ADD COLUMN IF NOT EXISTS source TEXT,                -- 'image_ocr' | 'text_input'
  ADD COLUMN IF NOT EXISTS model_provider TEXT,        -- 'azure_content_safety' | 'huggingface'
  ADD COLUMN IF NOT EXISTS model_label TEXT,           -- Model Classification Label
  ADD COLUMN IF NOT EXISTS model_score REAL,           -- Confidence Level/Score
  ADD COLUMN IF NOT EXISTS preview TEXT;               -- Short summary for front-end display

CREATE UNIQUE INDEX IF NOT EXISTS uniq_session_items
  ON session_items (session_id, content_hash);

CREATE INDEX IF NOT EXISTS idx_session_items_session_time
  ON session_items (session_id, created_at DESC);