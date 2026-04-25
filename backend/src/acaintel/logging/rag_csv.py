import csv
import os
from datetime import datetime

from src.acaintel.config import LOGS_DIR, RAG_LOG_CSV_PATH


def append_rag_log(query: str, results: list, prompt: str, answer: str) -> None:
    """Append one RAG interaction to CSV under backend/logs/."""
    os.makedirs(LOGS_DIR, exist_ok=True)

    file_exists = os.path.exists(RAG_LOG_CSV_PATH)

    retrieved_sources = " | ".join(
        f"{r['source']}:{r['chunk_id']}:{r['final_score']:.4f}"
        for r in results
    )

    with open(RAG_LOG_CSV_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "query",
                    "retrieved_sources",
                    "final_prompt",
                    "answer",
                ]
            )

        writer.writerow(
            [
                datetime.now().isoformat(),
                query,
                retrieved_sources,
                prompt,
                answer,
            ]
        )
