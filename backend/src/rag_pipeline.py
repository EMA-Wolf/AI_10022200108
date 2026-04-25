import os
import csv
from datetime import datetime

from hybrid_retriver import load_retriever_assets, retrieve_hybrid
from prompt_engineering import build_rag_prompt
from generator import generate_answer


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "rag_logs.csv")


def save_log(query, results, prompt, answer):
    os.makedirs(LOG_DIR, exist_ok=True)

    file_exists = os.path.exists(LOG_FILE)

    retrieved_sources = " | ".join([
        f"{r['source']}:{r['chunk_id']}:{r['final_score']:.4f}"
        for r in results
    ])

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "query",
                "retrieved_sources",
                "final_prompt",
                "answer"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            query,
            retrieved_sources,
            prompt,
            answer
        ])


def run_rag_query(query, index, chunks, model, top_k=5):
    retrieved_results = retrieve_hybrid(
        query=query,
        index=index,
        chunks=chunks,
        model=model,
        top_k=top_k,
        candidate_k=25
    )

    prompt = build_rag_prompt(query, retrieved_results)

    answer = generate_answer(prompt)

    save_log(query, retrieved_results, prompt, answer)

    return {
        "query": query,
        "retrieved_results": retrieved_results,
        "prompt": prompt,
        "answer": answer
    }


def print_rag_output(output):
    print("\n========== FINAL ANSWER ==========\n")
    print(output["answer"])

    print("\n========== RETRIEVED CHUNKS ==========\n")
    for i, result in enumerate(output["retrieved_results"], start=1):
        print(f"Result {i}")
        print(f"Final Score: {result['final_score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Text: {result['text'][:600]}...")
        print("-" * 90)

    print("\n========== FINAL PROMPT SENT TO LLM ==========\n")
    print(output["prompt"][:3000])


if __name__ == "__main__":
    index, chunks, model = load_retriever_assets()

    while True:
        user_query = input("\nAsk AcaIntel AI a question, or type 'exit': ")

        if user_query.lower().strip() == "exit":
            break

        output = run_rag_query(
            query=user_query,
            index=index,
            chunks=chunks,
            model=model,
            top_k=5
        )

        print_rag_output(output)