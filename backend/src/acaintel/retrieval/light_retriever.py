"""
Low-memory keyword retriever for constrained deployments.
Avoids FAISS and sentence-transformers at runtime.
"""

import json
import os
import re

from src.acaintel.config import COMBINED_CHUNKS_PATH


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


def load_light_assets():
    if not os.path.exists(COMBINED_CHUNKS_PATH):
        raise FileNotFoundError("Combined chunks not found. Run build_vector_index.py first.")

    with open(COMBINED_CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print("[SUCCESS] Light retriever assets loaded.")
    return chunks


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9%₵¢\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _keyword_score(query: str, text: str) -> float:
    query_terms = _normalize_text(query).split()
    text_normalized = _normalize_text(text)

    if not query_terms:
        return 0.0

    matches = 0
    for term in query_terms:
        if term in text_normalized:
            matches += 1

    return matches / len(query_terms)


def source_boost(query: str, source: str) -> float:
    query_normalized = _normalize_text(query)

    budget_hits = sum(1 for word in BUDGET_KEYWORDS if word in query_normalized)
    election_hits = sum(1 for word in ELECTION_KEYWORDS if word in query_normalized)

    if source == "Budget.pdf" and budget_hits >= election_hits:
        return 0.08

    if source == "Ghana_Election_Result.csv" and election_hits > budget_hits:
        return 0.08

    return 0.0


def exact_phrase_boost(query: str, text: str) -> float:
    query_normalized = _normalize_text(query)
    text_normalized = _normalize_text(text)

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


def retrieve_light(query: str, chunks: list, top_k: int = 5):
    results = []

    for chunk in chunks:
        text = chunk["text"]
        source = chunk["source"]

        kw_score = _keyword_score(query, text)
        boost_score = source_boost(query, source)
        phrase_score = exact_phrase_boost(query, text)

        # Light mode has no vector score.
        final_score = (0.85 * kw_score) + boost_score + phrase_score

        results.append(
            {
                "final_score": float(final_score),
                "vector_score": 0.0,
                "keyword_score": float(kw_score),
                "source_boost": float(boost_score),
                "phrase_boost": float(phrase_score),
                "chunk_id": chunk["chunk_id"],
                "source": source,
                "text": text,
                "metadata": chunk["metadata"],
            }
        )

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)
    return results[:top_k]
