from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.acaintel.api.deps import RagAssets, get_rag_assets
from src.acaintel.services.rag import run_rag_query

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(
    request: ChatRequest,
    assets: RagAssets = Depends(get_rag_assets),
):
    index, chunks, model = assets
    out = run_rag_query(
        request.query,
        index,
        chunks,
        model,
        top_k=5,
        candidate_k=25,
        log=True,
    )
    return {
        "query": out["query"],
        "answer": out["answer"],
        "retrieved_chunks": out["retrieved_results"],
        "final_prompt": out["prompt"],
    }
