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
CSV_PATH = BASE_DIR.parent / "waste_disposal_fee.csv"

MODEL_NAME = "jhgan/ko-sroberta-multitask"


def main():
    print("Loading data...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} items")

    # Preprocess: create structured text with labeled fields
    print("Preprocessing...")
    texts = df.apply(
        lambda row: f"품목: {row['대형폐기물명']} | 구분: {row['대형폐기물구분명']}",
        axis=1,
    ).tolist()

    print(f"Loading model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # Save embeddings
    DATA_DIR.mkdir(exist_ok=True)
    output_path = DATA_DIR / "embeddings.npy"
    np.save(output_path, embeddings)
    print(f"Saved embeddings to {output_path}")
    print(f"Shape: {embeddings.shape}")


if __name__ == "__main__":
    main()
