from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.hybrid_retriver import load_retriever_assets, retrieve_hybrid
from src.prompt_engineering import build_rag_prompt
from src.generator import generate_answer

app = FastAPI(title="AcaIntel AI RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your Vercel frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

index, chunks, model = load_retriever_assets()


class ChatRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {"message": "AcaIntel AI backend is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    results = retrieve_hybrid(
        query=request.query,
        index=index,
        chunks=chunks,
        model=model,
        top_k=5,
        candidate_k=25
    )

    prompt = build_rag_prompt(request.query, results)
    answer = generate_answer(prompt)

    return {
        "query": request.query,
        "answer": answer,
        "retrieved_chunks": results,
        "final_prompt": prompt
    }