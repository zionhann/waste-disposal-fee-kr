"""Generate embeddings for waste disposal items.

Usage:
    python scripts/generate_embeddings.py
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = BASE_DIR / "waste_disposal_fee.csv"

MODEL_NAME = "jhgan/ko-sroberta-multitask"
TEXT_TEMPLATE = "품목: {대형폐기물명} | 유의어: {대형폐기물특징}"


def main():
    print("Loading data...")
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    print(f"Loaded {len(df)} items")

    # Keep row filtering aligned with app/search.py (drop only missing names).
    print("Preprocessing...")
    df = df.dropna(subset=["대형폐기물명"]).copy()
    df["대형폐기물명"] = df["대형폐기물명"].astype(str).str.strip()
    df["대형폐기물특징"] = df["대형폐기물특징"].fillna("").astype(str).str.strip()
    print(f"Using text template: {TEXT_TEMPLATE}")
    texts = ("품목: " + df["대형폐기물명"] + " | 유의어: " + df["대형폐기물특징"]).tolist()

    print(f"Loading model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    # Save embeddings
    DATA_DIR.mkdir(exist_ok=True)
    output_path = DATA_DIR / "embeddings.npy"
    np.save(output_path, embeddings)
    print(f"Saved embeddings to {output_path}")
    print(f"Shape: {embeddings.shape}")


if __name__ == "__main__":
    main()
