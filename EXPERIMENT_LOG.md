# CS4241 RAG Experiment Log (Manual)

Student Name: `<Your Name>`  
Index Number: `<Your Index Number>`  
Repository: `<GitHub URL>`  
Deployed URL: `<App URL>`  
Date Range: `2026-04-25`

---

## 1) Objective

Evaluate real retrieval and answer behavior for a mixed-domain RAG assistant (Ghana election CSV + 2025 budget PDF), with focus on:

- retrieval relevance,
- hallucination control,
- impact of domain-specific scoring boosts.

---

## 2) Dataset and Setup Snapshot

| Item | Value |
|---|---|
| Election dataset source | `Ghana_Election_Result.csv` |
| Budget dataset source | `Budget.pdf` |
| Runtime retriever mode | `light` (keyword + boost scoring) |
| Embedding model (index build) | `all-MiniLM-L6-v2` |
| Vector store | `FAISS IndexFlatIP` (built successfully) |
| LLM | `llama-3.1-8b-instant` (Groq) |
| Top-k | `5` |
| Candidate-k | `25` |
| Temperature | `0.2` |

Notes:
- At runtime, `RETRIEVER_MODE` defaulted to `light`, so `vector_score=0.0` in live query outputs.
- Pipelines successfully produced: 615 election chunks, 337 budget chunks, 952 combined chunks.

---

## 3) Part A - Chunking Strategy Experiments

### 3.1 Chunking configurations tested

| Config ID | Dataset | Chunk size rule | Overlap | Metadata included | Reason for trying |
|---|---|---|---|---|---|
| A1 | Budget | 500 words | 80 words | source, page, chunk_size_words, overlap_words, document_type, chunk_type | Preserve policy context across boundaries |
| A2 | Budget | Manual high-value chunk (`budget_intro_theme`) | N/A | source, page, chunk_type=manual_intro_theme | Improve retrieval of budget theme/identity queries |
| A3 | Election | 1 row -> 1 chunk | N/A | source, year, candidate, party, votes, percentage, region, region_clean, category | Keep factual tabular records atomic |

### 3.2 Retrieval quality impact

| Query | Config | Retrieved relevance (1-5) | Observed issue | Improvement idea |
|---|---|---:|---|---|
| What is the theme of the 2025 budget? | A2 | 5 | None on top result | Keep manual intro chunk; retain phrase boost |
| What does the budget say about inflation? | A1 | 4 | Some non-inflation budget chunks still in top-k | Add reranker for tighter topicality |
| Who won in Ashanti Region? | A3 | 5 | None on top result | Keep row-level election chunks |

### 3.3 Conclusion

Best current strategy is modality-specific:
- election: row-level chunks for high factual precision,
- budget: overlapping chunks + manual intro chunk for continuity and key-theme capture.

---

## 4) Part B - Retrieval Failure Cases and Fixes

### 4.1 Baseline failure cases

| Case ID | Query | Why retrieval failed | Wrong/irrelevant chunks returned |
|---|---|---|---|
| B1 | Who won the 2025 election in Ashanti? | Query mixes election intent + year not represented in election source; light mode lexical match favored budget text | Top result from `Budget.pdf` (`budget_150`) instead of election source |
| B2 | What does the budget say about inflation? | Keyword-only matching in light mode includes broad budget sections with shared terms | Non-inflation budget chunks (e.g., education/conclusion sections) appeared in top-k |

### 4.2 Fixes implemented

| Fix ID | Change made in retrieval logic | File(s) touched | Expected effect |
|---|---|---|---|
| F1 | Added source-intent boost (budget vs election keyword hit counts) | `backend/src/acaintel/retrieval/hybrid_retriver.py`, `backend/src/acaintel/retrieval/light_retriever.py` | Push domain-aligned sources up |
| F2 | Added important phrase boost (`theme`, `who won`, `inflation rate`, etc.) | `backend/src/acaintel/retrieval/hybrid_retriver.py`, `backend/src/acaintel/retrieval/light_retriever.py` | Improve intent-specific ranking |

### 4.3 Before vs after evidence

Scoring view used (light mode):
- Before (baseline): `0.85 * keyword_score`
- After (current): `0.85 * keyword_score + source_boost + phrase_boost`

| Query | Baseline score (before) | After score (current) | Delta | Notes |
|---|---:|---:|---:|---|
| What is the theme of the 2025 budget? (`budget_intro_theme`) | 0.7438 | 0.9438 | +0.2000 | Gain from source + phrase boosts |
| What does the budget say about inflation? (`budget_82`) | 0.4857 | 0.5657 | +0.0800 | Source boost improved rank confidence |
| Who won in Ashanti Region? (`election_12`) | 0.5100 | 0.5900 | +0.0800 | Election source prioritized |
| Compare NPP and NDC votes. (`election_0`) | 0.3400 | 0.4200 | +0.0800 | Better election intent alignment |
| What is the most important policy? (`budget_16`) | 0.5667 | 0.6467 | +0.0800 | Mild gain; query remains ambiguous |
| Who won the 2025 election in Ashanti? (`budget_150`) | 0.6071 | 0.6071 | +0.0000 | Edge case where boosts did not fire |

---

## 5) Part C - Prompt Engineering Iterations

### 5.1 Prompt variants

| Prompt ID | Key prompt rule/change | Why changed |
|---|---|---|
| P1 | Context injection only (basic) | Initial baseline |
| P2 | Add strict anti-hallucination rule + abstain if missing evidence | Reduce unsupported answers |
| P3 | Add explicit source mention + ambiguity handling | Improve traceability and safe behavior |

### 5.2 Same-query comparison

| Query | Prompt ID | Response quality (1-5) | Hallucination risk (Low/Med/High) | Notes |
|---|---|---:|---|---|
| Who won the 2025 election in Ashanti? | P1 | 2 | High | Tended to over-commit |
| Who won the 2025 election in Ashanti? | P2 | 4 | Low | Abstained when evidence insufficient |
| Who won the 2025 election in Ashanti? | P3 | 4 | Low | Same safe abstention + clearer source behavior |

### 5.3 Conclusion

P3 performed best overall because it combines grounded answering with explicit abstention and source transparency.

---

## 6) Part D - Pipeline Trace Evidence

| Query ID | User query | Top retrieved source(s) | Score snapshot | Prompt captured? | Response acceptable? |
|---|---|---|---|---|---|
| D1 | What is the theme of the 2025 budget? | Budget.pdf (`budget_intro_theme`) | final=0.9438, kw=0.875, source_boost=0.08, phrase_boost=0.12 | Yes | Yes |
| D2 | Who won in Ashanti Region? | Ghana_Election_Result.csv (`election_12` etc.) | final=0.5900, kw=0.600, source_boost=0.08 | Yes | Yes |
| D3 | What does the budget say about inflation? | Budget.pdf (`budget_82`) | final=0.5657, kw=0.5714, source_boost=0.08 | Yes | Yes |

---

## 7) Part E - Adversarial Testing

| Adv ID | Query type | Query | Accuracy (1-5) | Hallucination noted? | Consistency across reruns |
|---|---|---|---:|---|---|
| E1 | Ambiguous | What is the most important policy? | 4 | No | Consistent abstention/qualification |
| E2 | Misleading/incomplete | Who won the 2025 election in Ashanti? | 3 | No | Consistent abstention despite retrieval mismatch |

### Observations

- Prompt safeguards held up under adversarial prompts (no fabricated winner for 2025 Ashanti query).
- Main weak point is retrieval source mismatch on mixed-intent adversarial queries in light mode.
- Next improvement: run runtime `hybrid` mode by setting `RETRIEVER_MODE=hybrid` in deployment/runtime env.

---

## 8) Part E - RAG vs Pure LLM Comparison

Pure LLM-only run was not executed in this measurement session.
This section remains pending if strict side-by-side scoring is required by examiner.

| Query | RAG answer quality (1-5) | Pure LLM quality (1-5) | Which was better? | Evidence |
|---|---:|---:|---|---|
| What is the theme of the 2025 budget? | 5 | N/A | RAG (measured) | Correct theme + source shown |
| Who won in Ashanti Region? | 5 | N/A | RAG (measured) | Correct candidate/votes/percentage from election source |
| Who won the 2025 election in Ashanti? | 3 | N/A | RAG (safe abstention) | Refused unsupported claim |

Conclusion:
- Measured RAG outputs are strongly grounded for in-domain factual queries.
- Pure LLM baseline should be run next for strict numeric comparison table if required.

---

## 9) Part F - Architecture Notes

- **Data flow:** User query -> API -> retrieval -> prompt builder -> LLM -> answer + logs.
- **Why suitable:** Handles structured (CSV) and unstructured (PDF) sources in one RAG flow with transparent evidence.
- **Trade-offs:** light mode improves deployment simplicity but can reduce adversarial retrieval robustness versus full hybrid mode.

Optional diagram reference:
- `Diagrams/Retrieval Scoring Logic (Innovation Diagram).drawio`

---

## 10) Part G - Innovation Component

Feature selected: `Domain-specific scoring function`

| Innovation detail | Implementation file(s) | Measured benefit |
|---|---|---|
| Source-intent boost (`Budget.pdf` vs election CSV) | `backend/src/acaintel/retrieval/hybrid_retriver.py`, `backend/src/acaintel/retrieval/light_retriever.py` | +0.08 score gain on multiple intent-aligned queries |
| Important phrase boost (e.g., budget theme) | `backend/src/acaintel/retrieval/hybrid_retriver.py`, `backend/src/acaintel/retrieval/light_retriever.py` | +0.20 gain on budget theme query top chunk |

---

## 11) Final Reflections

- Biggest technical challenge: dependency/runtime mode differences (`light` vs `hybrid`) and handling mixed-intent adversarial queries.
- Most effective improvement: domain-specific boosting (source + phrase), especially for budget theme and election intent alignment.
- What to improve next: run full runtime `hybrid` mode for production evaluation and add automated reranking to reduce residual top-k noise.

