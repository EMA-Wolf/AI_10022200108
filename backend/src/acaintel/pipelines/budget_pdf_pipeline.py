import os
import re
import json
import fitz  # PyMuPDF


from src.acaintel.config import (
    BUDGET_CHUNKS_OUTPUT_PATH,
    BUDGET_PDF_PATH,
    BUDGET_RAW_TEXT_PATH,
)


# =========================
# CONFIGURATION
# =========================

PDF_PATH = BUDGET_PDF_PATH
RAW_TEXT_OUTPUT_PATH = BUDGET_RAW_TEXT_PATH
CHUNKS_OUTPUT_PATH = BUDGET_CHUNKS_OUTPUT_PATH


# =========================
# STEP 1: LOAD AND EXTRACT PDF
# =========================

def extract_pdf_text(pdf_path):
    """
    Extracts text from the Budget PDF page by page.
    Each page is stored with page metadata.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"Budget PDF not found at {pdf_path}. "
            "Place Budget.pdf inside the data folder."
        )

    document = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")

        pages.append({
            "source": "Budget.pdf",
            "page": page_number,
            "text": text
        })

    print(f"[SUCCESS] Extracted text from {len(pages)} pages.")

    return pages


# =========================
# STEP 2: CLEAN TEXT
# =========================

def clean_pdf_text(text):
    """
    Cleans extracted PDF text by removing repeated spacing,
    page noise, and broken formatting.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("\n", " ")

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    # Fix broken hyphenated words
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

    # Remove repeated budget header/footer fragments
    text = text.replace("Resetting the Economy for the Ghana We Want", "")
    text = text.replace("2025 Budget", "")

    return text.strip()


def clean_pdf_pages(pages):
    """
    Applies cleaning to all extracted PDF pages.
    Removes empty pages.
    """

    cleaned_pages = []

    for page in pages:
        cleaned_text = clean_pdf_text(page["text"])

        if len(cleaned_text) > 50:
            cleaned_pages.append({
                "source": page["source"],
                "page": page["page"],
                "text": cleaned_text
            })

    print(f"[SUCCESS] Cleaned PDF pages. Usable pages: {len(cleaned_pages)}")

    return cleaned_pages


# =========================
# STEP 3: CHUNKING
# =========================

def split_words(text):
    """
    Splits text into words.
    """

    return text.split()


def create_overlapping_chunks(text, chunk_size=500, overlap=80):
    """
    Creates overlapping word-based chunks.

    chunk_size = number of words per chunk
    overlap = number of words repeated between chunks
    """

    words = split_words(text)
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text.strip()) > 100:
            chunks.append(chunk_text)

        start += chunk_size - overlap

    return chunks


# def create_budget_chunks(cleaned_pages, chunk_size=500, overlap=80):
#     """
#     Converts cleaned PDF pages into RAG chunks.
#     """

#     all_chunks = []
#     chunk_counter = 0

#     for page in cleaned_pages:
#         page_chunks = create_overlapping_chunks(
#             page["text"],
#             chunk_size=chunk_size,
#             overlap=overlap
#         )

#         for chunk_text in page_chunks:
#             chunk = {
#                 "chunk_id": f"budget_{chunk_counter}",
#                 "source": "Budget.pdf",
#                 "text": chunk_text,
#                 "metadata": {
#                     "source": "Budget.pdf",
#                     "page": page["page"],
#                     "chunk_size_words": chunk_size,
#                     "overlap_words": overlap,
#                     "document_type": "Ghana 2025 Budget Statement"
#                 }
#             }

#             all_chunks.append(chunk)
#             chunk_counter += 1

#     print(f"[SUCCESS] Created {len(all_chunks)} Budget PDF chunks.")

#     return all_chunks

def create_budget_chunks(cleaned_pages, chunk_size=500, overlap=80):
    """
    Converts cleaned PDF pages into RAG chunks.

    A manual intro/theme chunk is added first because the Budget theme appears
    in the document cover/intro area and may be missed by normal page chunking.
    """

    all_chunks = []
    chunk_counter = 0

    # Manual high-value chunk for important document identity/theme information
    intro_chunk = {
        "chunk_id": "budget_intro_theme",
        "source": "Budget.pdf",
        "text": (
            "The theme of the 2025 Budget Statement and Economic Policy of the Government "
            "of Ghana is 'Resetting the Economy for the Ghana We Want'. "
            "The Budget was presented to Parliament by Dr. Cassiel Ato Forson, Minister for Finance, "
            "on Tuesday March 11, 2025, under the authority of President John Dramani Mahama. "
            "The document is the Budget Statement and Economic Policy of the Government of Ghana "
            "for the 2025 Financial Year."
        ),
        "metadata": {
            "source": "Budget.pdf",
            "page": 1,
            "chunk_size_words": "manual",
            "overlap_words": "manual",
            "document_type": "Ghana 2025 Budget Statement",
            "chunk_type": "manual_intro_theme"
        }
    }

    all_chunks.append(intro_chunk)
    chunk_counter += 1

    # Normal PDF page-based chunking
    for page in cleaned_pages:
        page_chunks = create_overlapping_chunks(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        for chunk_text in page_chunks:
            chunk = {
                "chunk_id": f"budget_{chunk_counter}",
                "source": "Budget.pdf",
                "text": chunk_text,
                "metadata": {
                    "source": "Budget.pdf",
                    "page": page["page"],
                    "chunk_size_words": chunk_size,
                    "overlap_words": overlap,
                    "document_type": "Ghana 2025 Budget Statement",
                    "chunk_type": "pdf_page_chunk"
                }
            }

            all_chunks.append(chunk)
            chunk_counter += 1

    print(f"[SUCCESS] Created {len(all_chunks)} Budget PDF chunks.")

    return all_chunks


# =========================
# STEP 4: SAVE OUTPUTS
# =========================

def save_outputs(cleaned_pages, chunks):
    """
    Saves raw cleaned text and JSON chunks.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(RAW_TEXT_OUTPUT_PATH, "w", encoding="utf-8") as file:
        for page in cleaned_pages:
            file.write(f"\n\n--- PAGE {page['page']} ---\n")
            file.write(page["text"])

    with open(CHUNKS_OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)

    print(f"[SUCCESS] Cleaned Budget text saved to: {RAW_TEXT_OUTPUT_PATH}")
    print(f"[SUCCESS] Budget chunks saved to: {CHUNKS_OUTPUT_PATH}")


# =========================
# STEP 5: FULL PIPELINE
# =========================

def run_budget_pdf_pipeline():
    """
    Runs full Budget PDF processing pipeline:
    extract → clean → chunk → save.
    """

    print("\n========== BUDGET PDF PIPELINE STARTED ==========\n")

    pages = extract_pdf_text(PDF_PATH)
    cleaned_pages = clean_pdf_pages(pages)
    chunks = create_budget_chunks(cleaned_pages)
    save_outputs(cleaned_pages, chunks)

    print("\n========== BUDGET PDF PIPELINE COMPLETED ==========\n")

    return cleaned_pages, chunks


# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":
    cleaned_pages, chunks = run_budget_pdf_pipeline()

    print("\nSample cleaned page:")
    print(cleaned_pages[0]["text"][:1000])

    print("\nSample chunk:")
    print(json.dumps(chunks[0], indent=4, ensure_ascii=False))