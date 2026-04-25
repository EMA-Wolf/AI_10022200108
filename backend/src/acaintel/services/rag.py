from src.acaintel.generation.prompt_engineering import build_rag_prompt
from src.acaintel.generation.generator import generate_answer
from src.acaintel.logging.rag_csv import append_rag_log


def run_rag_query(
    query: str,
    assets,
    *,
    top_k: int = 5,
    candidate_k: int = 25,
    log: bool = True,
) -> dict:
    """
    Retrieve → build prompt → generate answer.
    Optionally append a row to logs/rag_logs.csv.
    """
    retrieve_fn = assets["retrieve_fn"]
    chunks = assets["chunks"]
    mode = assets.get("mode", "light")

    if mode == "hybrid":
        retrieved_results = retrieve_fn(
            query=query,
            index=assets["index"],
            chunks=chunks,
            model=assets["model"],
            top_k=top_k,
            candidate_k=candidate_k,
        )
    else:
        retrieved_results = retrieve_fn(
            query=query,
            chunks=chunks,
            top_k=top_k,
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
