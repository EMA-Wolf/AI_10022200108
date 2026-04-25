from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.acaintel.api.routes.chat import router as chat_router

app = FastAPI(title="AcaIntel AI RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def home():
    return {"message": "AcaIntel AI backend is running"}
