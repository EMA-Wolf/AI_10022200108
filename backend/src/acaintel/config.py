"""
Paths and constants resolved from the backend root (parent of `src/`).
Works regardless of current working directory when running uvicorn or pipelines.
"""

from pathlib import Path

# backend/src/acaintel/config.py -> parents[2] == backend/
BACKEND_ROOT: Path = Path(__file__).resolve().parents[2]

DATA_DIR: Path = BACKEND_ROOT / "data"
PROCESSED_DIR: Path = BACKEND_ROOT / "processed"
VECTOR_STORE_DIR: Path = BACKEND_ROOT / "vector_store"
LOGS_DIR: Path = BACKEND_ROOT / "logs"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Vector store / retrieval
FAISS_INDEX_PATH = str(VECTOR_STORE_DIR / "faiss_index.index")
COMBINED_CHUNKS_PATH = str(VECTOR_STORE_DIR / "combined_chunks.json")
EMBEDDINGS_PATH = str(VECTOR_STORE_DIR / "embeddings.pkl")

# Pipelines → build index
ELECTION_CHUNKS_PATH = str(PROCESSED_DIR / "ghana_election_chunks.json")
BUDGET_CHUNKS_PATH = str(PROCESSED_DIR / "budget_chunks.json")

# Election pipeline
ELECTION_CSV_PATH = str(DATA_DIR / "Ghana_Election_Result.csv")
ELECTION_CLEAN_CSV_PATH = str(PROCESSED_DIR / "ghana_election_clean.csv")
ELECTION_CHUNKS_OUTPUT_PATH = str(PROCESSED_DIR / "ghana_election_chunks.json")

# Budget pipeline
BUDGET_PDF_PATH = str(DATA_DIR / "Budget.pdf")
BUDGET_RAW_TEXT_PATH = str(PROCESSED_DIR / "budget_raw_text.txt")
BUDGET_CHUNKS_OUTPUT_PATH = str(PROCESSED_DIR / "budget_chunks.json")

# Logging
RAG_LOG_CSV_PATH = str(LOGS_DIR / "rag_logs.csv")
