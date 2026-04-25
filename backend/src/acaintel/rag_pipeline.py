from src.acaintel.retrieval.hybrid_retriver import load_retriever_assets
from src.acaintel.services.rag import run_rag_query


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
            user_query,
            index,
            chunks,
            model,
            top_k=5,
            candidate_k=25,
            log=True,
        )

        print_rag_output(output)
