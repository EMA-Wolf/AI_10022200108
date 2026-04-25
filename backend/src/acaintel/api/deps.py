from functools import lru_cache
from typing import Any, Tuple

from src.acaintel.retrieval.hybrid_retriver import load_retriever_assets

# (faiss.Index, list of chunks, SentenceTransformer)
RagAssets = Tuple[Any, list, Any]


@lru_cache(maxsize=1)
def _load_retriever_assets_cached() -> RagAssets:
    return load_retriever_assets()


def get_rag_assets() -> RagAssets:
    """FastAPI dependency: load FAISS + chunks + embedding model once per process."""
    return _load_retriever_assets_cached()
