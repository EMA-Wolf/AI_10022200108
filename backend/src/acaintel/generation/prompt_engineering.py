def build_context_from_results(results, max_chars=4500):
    context_parts = []
    total_chars = 0

    for i, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})
        source = result.get("source", "Unknown")
        page = metadata.get("page", "N/A")

        score = result.get("final_score", result.get("score", 0))

        context_block = (
            f"[Context {i}]\n"
            f"Source: {source}\n"
            f"Page/Metadata: {page}\n"
            f"Similarity Score: {score:.4f}\n"
            f"Text: {result['text']}\n"
        )

        if total_chars + len(context_block) > max_chars:
            break

        context_parts.append(context_block)
        total_chars += len(context_block)

    return "\n\n".join(context_parts)


def build_rag_prompt(user_query, retrieved_results):
    context = build_context_from_results(retrieved_results)

    return f"""
You are AcaIntel AI, a Retrieval-Augmented Generation assistant for Academic City University.

Answer using ONLY the retrieved context.

Rules:
1. Do not invent facts.
2. If the answer is not in the context, say: "I could not find enough evidence in the provided documents."
3. If the question is ambiguous, explain what is missing.
4. Mention the source used.
5. Use clear academic language.

Retrieved Context:
{context}

User Question:
{user_query}

Final Answer:
""".strip()