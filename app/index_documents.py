
import json
from pathlib import Path

from app.embeddings import generate_embeddings
from app.vector_store import initialize_database, store_chunks

CHUNKS_FILE = Path("data/processed/chunks.jsonl")
BATCH_SIZE = 32


def main():
    chunks = [
        json.loads(line)
        for line in CHUNKS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    initialize_database()

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        embeddings = generate_embeddings([chunk["text"] for chunk in batch])

        for chunk, embedding in zip(batch, embeddings, strict=True):
            chunk["embedding"] = embedding

        store_chunks(batch)
        print(f"Stored {min(start + len(batch), len(chunks))}/{len(chunks)} chunks")

    print("Document indexing completed successfully!")


if __name__ == "__main__":
    main()

