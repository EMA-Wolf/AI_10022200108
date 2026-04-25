import os
import re
import json
import pandas as pd


# =========================
# CONFIGURATION
# =========================

DATA_DIR = "data"
OUTPUT_DIR = "processed"

# Put your downloaded CSV inside the data folder with this name
LOCAL_CSV_PATH = os.path.join(DATA_DIR, "Ghana_Election_Result.csv")

CLEAN_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "ghana_election_clean.csv")
CHUNKS_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "ghana_election_chunks.json")


# =========================
# STEP 1: LOAD LOCAL DATASET
# =========================

def load_local_election_data():
    """
    Loads the Ghana Election Result CSV dataset from your local machine.
    Make sure the file is saved as:
    data/Ghana_Election_Result.csv
    """

    if not os.path.exists(LOCAL_CSV_PATH):
        raise FileNotFoundError(
            f"CSV file not found at {LOCAL_CSV_PATH}. "
            "Create a data folder and place Ghana_Election_Result.csv inside it."
        )

    # Read with header so named CSV columns can be mapped correctly.
    df = pd.read_csv(LOCAL_CSV_PATH)

    print(f"[SUCCESS] Local election dataset loaded from: {LOCAL_CSV_PATH}")
    print(f"[INFO] Raw dataset shape: {df.shape}")

    return df


# =========================
# STEP 2: CLEANING HELPERS
# =========================

def clean_text(value):
    if pd.isna(value):
        return ""

    value = str(value)
    value = value.replace("\xa0", " ")
    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_votes(value):
    if pd.isna(value):
        return 0

    value = str(value)
    value = value.replace(",", "")
    value = re.sub(r"[^0-9]", "", value)

    if value == "":
        return 0

    return int(value)


def clean_percentage(value):
    if pd.isna(value):
        return 0.0

    value = str(value)
    value = str(value).replace("%", "").strip()

    try:
        return float(value)
    except ValueError:
        return 0.0


def clean_year(value):
    if pd.isna(value):
        return None

    value = str(value)
    match = re.search(r"\d{4}", value)

    if match:
        return int(match.group())

    return None


# =========================
# STEP 3: STRUCTURE DATASET
# =========================

def structure_election_data(df):
    expected_columns = [
        "candidate",
        "party",
        "votes",
        "percentage",
        "year",
        "region",
        "region_clean",
        "category"
    ]

    # Support the current source CSV format:
    # Year, Old Region, New Region, Code, Candidate, Party, Votes, Votes(%)
    source_to_expected = {
        "year": "year",
        "old region": "region",
        "new region": "region_clean",
        "code": "category",
        "candidate": "candidate",
        "party": "party",
        "votes": "votes",
        "votes(%)": "percentage",
    }

    normalized_cols = {str(c).strip().lower(): c for c in df.columns}

    if all(src_col in normalized_cols for src_col in source_to_expected):
        rename_map = {
            normalized_cols[src_col]: dst_col
            for src_col, dst_col in source_to_expected.items()
        }
        df = df.rename(columns=rename_map)[expected_columns].copy()
    else:
        # Fallback for headerless files already aligned by position.
        if df.shape[1] != len(expected_columns):
            raise ValueError(
                f"Expected {len(expected_columns)} columns, but found {df.shape[1]} columns. "
                "Open the CSV and confirm the column structure."
            )
        df.columns = expected_columns

    text_columns = [
        "candidate",
        "party",
        "region",
        "region_clean",
        "category"
    ]

    for col in text_columns:
        df[col] = df[col].apply(clean_text)

    df["votes"] = df["votes"].apply(clean_votes)
    df["percentage"] = df["percentage"].apply(clean_percentage)
    df["year"] = df["year"].apply(clean_year)

    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    df = df[df["candidate"] != ""]
    df = df[df["party"] != ""]
    df = df[df["region"] != ""]

    df = df.drop_duplicates().reset_index(drop=True)

    print("[SUCCESS] Election dataset cleaned and structured.")
    print(f"[INFO] Cleaned dataset shape: {df.shape}")

    return df


# =========================
# STEP 4: ADD RAG TEXT
# =========================

def add_derived_fields(df):
    df["source"] = "Ghana_Election_Result.csv"

    df["search_text"] = df.apply(
        lambda row: (
            f"In {row['year']}, {row['candidate']} of {row['party']} "
            f"received {row['votes']} votes, representing {row['percentage']}%, "
            f"in {row['region']} region. "
            f"The record category is {row['category']}."
        ),
        axis=1
    )

    print("[SUCCESS] Search text created for RAG retrieval.")

    return df


# =========================
# STEP 5: CREATE CHUNKS
# =========================

def create_election_chunks(df):
    chunks = []

    for index, row in df.iterrows():
        chunks.append({
            "chunk_id": f"election_{index}",
            "source": row["source"],
            "text": row["search_text"],
            "metadata": {
                "source": row["source"],
                "year": int(row["year"]),
                "candidate": row["candidate"],
                "party": row["party"],
                "votes": int(row["votes"]),
                "percentage": float(row["percentage"]),
                "region": row["region"],
                "region_clean": row["region_clean"],
                "category": row["category"]
            }
        })

    print(f"[SUCCESS] Created {len(chunks)} election chunks.")

    return chunks


# =========================
# STEP 6: SAVE OUTPUTS
# =========================

def save_clean_data(df, chunks):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df.to_csv(CLEAN_OUTPUT_PATH, index=False)

    with open(CHUNKS_OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)

    print(f"[SUCCESS] Clean CSV saved to: {CLEAN_OUTPUT_PATH}")
    print(f"[SUCCESS] Chunks saved to: {CHUNKS_OUTPUT_PATH}")


# =========================
# STEP 7: RUN FULL PIPELINE
# =========================

def run_election_pipeline():
    print("\n========== GHANA ELECTION DATA PIPELINE STARTED ==========\n")

    raw_df = load_local_election_data()
    clean_df = structure_election_data(raw_df)
    clean_df = add_derived_fields(clean_df)
    chunks = create_election_chunks(clean_df)
    save_clean_data(clean_df, chunks)

    print("\n========== GHANA ELECTION DATA PIPELINE COMPLETED ==========\n")

    return clean_df, chunks


if __name__ == "__main__":
    clean_df, chunks = run_election_pipeline()

    print("\nSample cleaned records:")
    print(clean_df.head())

    print("\nSample chunk:")
    if chunks:
        print(json.dumps(chunks[0], indent=4, ensure_ascii=False))
    else:
        print("No chunks created. Check input data and filtering steps.")