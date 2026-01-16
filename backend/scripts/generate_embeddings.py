"""Generate embeddings for waste disposal items.

Usage:
    python scripts/generate_embeddings.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = BASE_DIR.parent / "waste_disposal_fee.csv"


def main():
    print("Loading data...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} items")

    # Preprocess: combine name and category with [SEP] token
    print("Preprocessing...")
    texts = df.apply(
        lambda row: f"{row['대형폐기물명']} [SEP] {row['대형폐기물구분명']}",
        axis=1
    ).tolist()

    print("Loading model (jhgan/ko-sbert-sts)...")
    model = SentenceTransformer("jhgan/ko-sbert-sts")

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
