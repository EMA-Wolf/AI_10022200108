"""
Purpose:
Hybrid retriever using FAISS vector similarity + keyword scoring + source boosting.
"""

import os
import re
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.acaintel.config import (
    COMBINED_CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
)


BUDGET_KEYWORDS = [
    "budget", "economy", "inflation", "gdp", "debt", "policy",
    "revenue", "expenditure", "fiscal", "macroeconomic", "theme",
    "ghana", "2025", "finance", "mahama"
]

ELECTION_KEYWORDS = [
    "election", "votes", "vote", "candidate", "party", "npp", "ndc",
    "cpp", "region", "ashanti", "volta", "greater accra", "winner",
    "won", "percentage", "constituency"
]


def load_retriever_assets():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError("FAISS index not found. Run build_vector_index.py first.")

    if not os.path.exists(COMBINED_CHUNKS_PATH):
        raise FileNotFoundError("Combined chunks not found. Run build_vector_index.py first.")

    index = faiss.read_index(FAISS_INDEX_PATH)

    with open(COMBINED_CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("[SUCCESS] Hybrid retriever assets loaded.")

    return index, chunks, model


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9%₵¢\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def keyword_score(query, text):
    query_terms = normalize_text(query).split()
    text_normalized = normalize_text(text)

    if not query_terms:
        return 0.0

    matches = 0

    for term in query_terms:
        if term in text_normalized:
            matches += 1

    return matches / len(query_terms)


def keyword_score(query, text):
    query_terms = normalize_text(query).split()
    text_normalized = normalize_text(text)

    if not query_terms:
        return 0.0

    matches = 0

    for term in query_terms:
        if term in text_normalized:
            matches += 1

    return matches / len(query_terms)


def exact_phrase_boost(query, text):
    query_normalized = normalize_text(query)
    text_normalized = normalize_text(text)

    important_phrases = [
        "theme of the 2025 budget",
        "2025 budget",
        "resetting the economy",
        "ghana we want",
        "who won",
        "received votes",
        "inflation rate",
        "public debt",
        "macroeconomic targets"
    ]

    boost = 0.0

    for phrase in important_phrases:
        if phrase in query_normalized and phrase.replace("the ", "") in text_normalized:
            boost += 0.12

    if query_normalized in text_normalized:
        boost += 0.15

    return boost


def retrieve_hybrid(query, index, chunks, model, top_k=5, candidate_k=20):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    query_embedding = np.array(query_embedding).astype("float32")

    vector_scores, indices = index.search(query_embedding, candidate_k)

    results = []

    for vector_score, idx in zip(vector_scores[0], indices[0]):
        if idx == -1:
            continue

        chunk = chunks[idx]
        text = chunk["text"]
        source = chunk["source"]

        kw_score = keyword_score(query, text)
        boost_score = source_boost(query, source)
        phrase_score = exact_phrase_boost(query, text)

        final_score = (
            0.70 * float(vector_score)
            + 0.20 * kw_score
            + boost_score
            + phrase_score
        )

        results.append({
            "final_score": float(final_score),
            "vector_score": float(vector_score),
            "keyword_score": float(kw_score),
            "source_boost": float(boost_score),
            "phrase_boost": float(phrase_score),
            "chunk_id": chunk["chunk_id"],
            "source": source,
            "text": text,
            "metadata": chunk["metadata"]
        })

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    return results[:top_k]


def print_hybrid_results(query, results):
    print("\n========== HYBRID RETRIEVAL RESULTS ==========")
    print(f"Query: {query}\n")

    for i, result in enumerate(results, start=1):
        print(f"Result {i}")
        print(f"Final Score: {result['final_score']:.4f}")
        print(f"Vector Score: {result['vector_score']:.4f}")
        print(f"Keyword Score: {result['keyword_score']:.4f}")
        print(f"Source Boost: {result['source_boost']:.4f}")
        print(f"Phrase Boost: {result['phrase_boost']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Text: {result['text'][:700]}...")
        print("-" * 90)


if __name__ == "__main__":
    index, chunks, model = load_retriever_assets()

    while True:
        query = input("\nAsk a question, or type 'exit': ")

        if query.lower().strip() == "exit":
            break

        results = retrieve_hybrid(
            query=query,
            index=index,
            chunks=chunks,
            model=model,
            top_k=5,
            candidate_k=25
        )

        print_hybrid_results(query, results)