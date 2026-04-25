from src.acaintel.retrieval.hybrid_retriver import retrieve_hybrid
from src.acaintel.generation.prompt_engineering import build_rag_prompt
from src.acaintel.generation.generator import generate_answer
from src.acaintel.logging.rag_csv import append_rag_log


def run_rag_query(
    query: str,
    index,
    chunks: list,
    model,
    *,
    top_k: int = 5,
    candidate_k: int = 25,
    log: bool = True,
) -> dict:
    """
    Retrieve → build prompt → generate answer.
    Optionally append a row to logs/rag_logs.csv.
    """
    retrieved_results = retrieve_hybrid(
        query=query,
        index=index,
        chunks=chunks,
        model=model,
        top_k=top_k,
        candidate_k=candidate_k,
    )

    prompt = build_rag_prompt(query, retrieved_results)
    answer = generate_answer(prompt)

    if log:
        append_rag_log(query, retrieved_results, prompt, answer)

    return {
        "query": query,
        "retrieved_results": retrieved_results,
        "prompt": prompt,
        "answer": answer,
    }
