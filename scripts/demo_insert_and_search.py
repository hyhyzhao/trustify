import os, psycopg
from openai import AzureOpenAI
from pgvector.psycopg import register_vector, Vector  # ← 多引入 Vector

DB_URL = os.getenv("DATABASE_URL", "postgresql://cyberdev:devpass@127.0.0.1:5433/cyber_safe")
client = AzureOpenAI(
    api_key=os.environ["AOAI_KEY"],
    azure_endpoint=os.environ["AOAI_EP"],
    api_version="2024-02-15-preview",
)
deploy = os.getenv("AOAI_EMB_DEPLOY", "emb-small")

text = "sample text to embed"
emb = client.embeddings.create(model=deploy, input=text).data[0].embedding  # 1536

with psycopg.connect(DB_URL) as conn:
    register_vector(conn)  # 让 psycopg 认识 pgvector 类型
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO session_items (session_id, kind, content_text, embedding)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, ("demo-1", "text", text, emb))
        print("Inserted:", cur.fetchone()[0])
        conn.commit()

        cur.execute("SET ivfflat.probes = 10")  # 可选：提升召回
        qvec = Vector(emb)                      # ← 关键：把查询向量包成 Vector

        cur.execute("""
            SELECT id, session_id, kind,
                   1 - (embedding <=> %s) AS cosine_sim
            FROM session_items
            WHERE deleted_at IS NULL
            ORDER BY embedding <=> %s
            LIMIT 5;
        """, (qvec, qvec))
        print("Top matches:", cur.fetchall())

