import os
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from src.acaintel.config import (
    BUDGET_CHUNKS_PATH,
    COMBINED_CHUNKS_PATH,
    ELECTION_CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    EMBEDDINGS_PATH,
    FAISS_INDEX_PATH,
    VECTOR_STORE_DIR,
)


# =========================
# LOAD CHUNKS
# =========================

def load_json_chunks(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Chunk file not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def combine_chunks():
    election_chunks = load_json_chunks(ELECTION_CHUNKS_PATH)
    budget_chunks = load_json_chunks(BUDGET_CHUNKS_PATH)

    combined_chunks = election_chunks + budget_chunks

    print(f"[INFO] Election chunks: {len(election_chunks)}")
    print(f"[INFO] Budget chunks: {len(budget_chunks)}")
    print(f"[SUCCESS] Combined chunks: {len(combined_chunks)}")

    return combined_chunks


# =========================
# EMBEDDINGS
# =========================

def create_embeddings(chunks):
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [chunk["text"] for chunk in chunks]

    print("[INFO] Generating embeddings...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.array(embeddings).astype("float32")

    print(f"[SUCCESS] Embeddings generated. Shape: {embeddings.shape}")

    return embeddings


# =========================
# BUILD FAISS INDEX
# =========================

def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(f"[SUCCESS] FAISS index built with {index.ntotal} vectors.")

    return index


# =========================
# SAVE OUTPUTS
# =========================

def save_vector_store(chunks, embeddings, index):
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

    with open(COMBINED_CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)

    with open(EMBEDDINGS_PATH, "wb") as file:
        pickle.dump(embeddings, file)

    faiss.write_index(index, FAISS_INDEX_PATH)

    print(f"[SUCCESS] Combined chunks saved to: {COMBINED_CHUNKS_PATH}")
    print(f"[SUCCESS] Embeddings saved to: {EMBEDDINGS_PATH}")
    print(f"[SUCCESS] FAISS index saved to: {FAISS_INDEX_PATH}")


# =========================
# FULL PIPELINE
# =========================

def run_vector_index_pipeline():
    print("\n========== VECTOR INDEX PIPELINE STARTED ==========\n")

    chunks = combine_chunks()
    embeddings = create_embeddings(chunks)
    index = build_faiss_index(embeddings)
    save_vector_store(chunks, embeddings, index)

    print("\n========== VECTOR INDEX PIPELINE COMPLETED ==========\n")


if __name__ == "__main__":
    run_vector_index_pipeline()