
import os

import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "callshield"),
        user=os.getenv("POSTGRES_USER", "callshield"),
        password=os.getenv("POSTGRES_PASSWORD", "callshield_local_password"),
    )


def initialize_database():
    with get_connection() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_id TEXT PRIMARY KEY,
                source_file TEXT NOT NULL,
                source_hash TEXT,
                file_type TEXT,
                page INTEGER,
                content TEXT NOT NULL,
                embedding VECTOR(384) NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
            ON document_chunks
            USING hnsw (embedding vector_cosine_ops)
        """)


def store_chunks(chunks):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO document_chunks
                (chunk_id, source_file, source_hash, file_type, page, content, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    source_hash = EXCLUDED.source_hash,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding
                """,
                [
                    (
                        chunk["chunk_id"],
                        chunk["source_file"],
                        chunk["source_hash"],
                        chunk["file_type"],
                        chunk["page"],
                        chunk["text"],
                        "[" + ",".join(map(str, chunk["embedding"])) + "]",
                    )
                    for chunk in chunks
                ],
            )


def search_chunks(query_embedding, limit=5):
    vector = "[" + ",".join(map(str, query_embedding)) + "]"

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT source_file, page, content,
                   embedding <=> %s::vector AS distance
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (vector, vector, limit),
        ).fetchall()

    return [
        {
            "source_file": row[0],
            "page": row[1],
            "content": row[2],
            "distance": row[3],
        }
        for row in rows
    ]
