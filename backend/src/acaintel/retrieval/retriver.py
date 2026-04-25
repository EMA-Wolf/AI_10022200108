import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.acaintel.config import (
    COMBINED_CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
)


def load_retriever_assets():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError("FAISS index not found. Run build_vector_index.py first.")

    if not os.path.exists(COMBINED_CHUNKS_PATH):
        raise FileNotFoundError("Combined chunks not found. Run build_vector_index.py first.")

    index = faiss.read_index(FAISS_INDEX_PATH)

    with open(COMBINED_CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("[SUCCESS] Retriever assets loaded.")

    return index, chunks, model


def retrieve_top_k(query, index, chunks, model, top_k=5):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    query_embedding = np.array(query_embedding).astype("float32")

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        chunk = chunks[idx]

        results.append({
            "score": float(score),
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "text": chunk["text"],
            "metadata": chunk["metadata"]
        })

    return results


def print_retrieval_results(query, results):
    print("\n========== RETRIEVAL RESULTS ==========")
    print(f"Query: {query}\n")

    for i, result in enumerate(results, start=1):
        print(f"Result {i}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Text: {result['text'][:500]}...")
        print("-" * 80)


if __name__ == "__main__":
    index, chunks, model = load_retriever_assets()

    while True:
        query = input("\nAsk a question, or type 'exit': ")

        if query.lower() == "exit":
            break

        results = retrieve_top_k(
            query=query,
            index=index,
            chunks=chunks,
            model=model,
            top_k=5
        )

        print_retrieval_results(query, results)