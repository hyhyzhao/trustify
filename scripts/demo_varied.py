import os, psycopg, hashlib
from openai import AzureOpenAI
from pgvector.psycopg import register_vector, Vector

DB_URL = os.getenv("DATABASE_URL", "postgresql://cyberdev:devpass@127.0.0.1:5433/cyber_safe")
client = AzureOpenAI(
    api_key=os.environ["AOAI_KEY"],
    azure_endpoint=os.environ["AOAI_EP"],
    api_version="2024-02-15-preview",
)
DEPLOY = os.getenv("AOAI_EMB_DEPLOY", "emb-small")

texts = [
    "You are such a loser, nobody likes you.",     # 明显侮辱
    "Let's meet at 3 PM near the library.",        # 中性安排
    "Great job on your presentation! Proud of you",# 正向鼓励
    "Go back to where you came from.",             # 伤害性/排外
    "Can you help me with the math homework?"      # 求助
]

def embed(t: str):
    return client.embeddings.create(model=DEPLOY, input=t).data[0].embedding

def sha256_bytes(t: str) -> bytes:
    return hashlib.sha256(t.lower().encode("utf-8")).digest()

with psycopg.connect(DB_URL) as conn:
    register_vector(conn)
    with conn.cursor() as cur:
        # 可选：建去重列和唯一索引（第一次跑需要；之后会“已存在”忽略）
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        cur.execute("ALTER TABLE session_items ADD COLUMN IF NOT EXISTS content_hash bytea;")
        cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='uniq_session_items') THEN "
                    "CREATE UNIQUE INDEX uniq_session_items ON session_items (session_id, content_hash); END IF; END $$;")
        conn.commit()

        # 批量插入（带去重：同 session + 同文本只插一次）
        for t in texts:
            v = embed(t)
            h = sha256_bytes(t)
            cur.execute("""
                INSERT INTO session_items (session_id, kind, content_text, embedding, content_hash)
                VALUES (%s, 'text', %s, %s, %s)
                ON CONFLICT (session_id, content_hash) DO NOTHING
                RETURNING id
            """, ("sess-var-1", t, Vector(v), h))
            rid = cur.fetchone()[0] if cur.rowcount else None
            print("Inserted:", rid, "|", t[:50])
        conn.commit()

        # 提升召回
        cur.execute("SET ivfflat.probes = 20")

        # 查询：用余弦距离 <=> ，相似度 = 1 - 距离
        query = "This is a mean and insulting comment."
        qvec = Vector(embed(query))
        cur.execute("""
            SELECT id,
                   LEFT(content_text, 60) AS preview,
                   1 - (embedding <=> %s) AS cosine_sim
            FROM session_items
            WHERE embedding IS NOT NULL AND deleted_at IS NULL
            ORDER BY embedding <=> %s
            LIMIT 5
        """, (qvec, qvec))
        print("\nQuery:", query)
        for r in cur.fetchall():
            print(r)
