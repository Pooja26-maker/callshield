from app.embeddings import generate_embeddings
from app.vector_store import search_chunks

query = "I lost my mobile phone. How can I block it?"
embedding = generate_embeddings([query])[0]
results = search_chunks(embedding)

for index, result in enumerate(results, start=1):
    print(f"\nResult {index}")
    print("Source:", result["source_file"])
    print("Page:", result["page"])
    print("Content:", result["content"][:300])
    print("Distance:", round(result["distance"], 4))
