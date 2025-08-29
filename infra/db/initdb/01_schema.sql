CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS flagged_content (
  id             BIGSERIAL PRIMARY KEY,
  risk_level     VARCHAR(16) NOT NULL,
  top_category   VARCHAR(64),
  top_confidence REAL,
  blob_container TEXT,
  blob_name      TEXT,
  mime_type      TEXT,
  embedding      VECTOR(768) NOT NULL,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Build a vector index when more data is available
-- CREATE INDEX idx_flagged_embedding_ivfflat
--   ON flagged_content USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_flagged_risk_created
  ON flagged_content (risk_level, created_at DESC);
