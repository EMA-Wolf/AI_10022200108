from functools import lru_cache
from typing import Any, Dict

from src.acaintel.config import RETRIEVER_MODE

# Generic runtime assets container for both modes.
RagAssets = Dict[str, Any]


@lru_cache(maxsize=1)
def _load_retriever_assets_cached() -> RagAssets:
    if RETRIEVER_MODE == "hybrid":
        # Imported lazily so light mode does not load torch/sentence-transformers.
        from src.acaintel.retrieval.hybrid_retriver import (
            load_retriever_assets,
            retrieve_hybrid,
        )

        index, chunks, model = load_retriever_assets()
        return {
            "mode": "hybrid",
            "index": index,
            "chunks": chunks,
            "model": model,
            "retrieve_fn": retrieve_hybrid,
        }

    from src.acaintel.retrieval.light_retriever import load_light_assets, retrieve_light

    chunks = load_light_assets()
    return {
        "mode": "light",
        "chunks": chunks,
        "retrieve_fn": retrieve_light,
    }


def get_rag_assets() -> RagAssets:
    """FastAPI dependency: load retrieval assets once per process."""
    return _load_retriever_assets_cached()
