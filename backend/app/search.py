import logging
import time

import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = BASE_DIR / "waste_disposal_fee.csv"

MODEL_NAME = "jhgan/ko-sroberta-multitask"

model: SentenceTransformer | None = None
embeddings: np.ndarray | None = None
df: pd.DataFrame | None = None


def load_resources():
    """Load model, embeddings, and CSV at startup."""
    global model, embeddings, df

    t0 = time.time()
    logger.info("Loading resources...")

    try:
        model = SentenceTransformer(MODEL_NAME)

        embeddings_path = DATA_DIR / "embeddings.npy"
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings not found at {embeddings_path}")
        embeddings = np.load(embeddings_path)

        if not CSV_PATH.exists():
            raise FileNotFoundError(f"CSV not found at {CSV_PATH}")
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        df["대형폐기물규격"] = df["대형폐기물규격"].fillna("")
        df["수수료"] = df["수수료"].fillna(0).astype(int)

        if embeddings.shape[0] != len(df):
            raise ValueError(
                f"Row count mismatch: {embeddings.shape[0]} embeddings vs {len(df)} CSV rows "
                f"(embeddings: {embeddings_path}, csv: {CSV_PATH})"
            )

        if embeddings.shape[1] != 768:
            raise ValueError(f"Embedding dim mismatch: expected 768, got {embeddings.shape[1]}")

        logger.info(f"Loaded {len(df)} items in {time.time() - t0:.2f}s")
    except Exception as e:
        logger.error(f"Failed to load resources: {e}")
        raise


def get_locations() -> dict:
    """Get unique sido and sigungu values."""
    if df is None:
        return {"sido": [], "sigungu": {}}
    return {
        "sido": sorted(df["시도명"].unique().tolist()),
        "sigungu": df.groupby("시도명")["시군구명"].unique().apply(list).to_dict(),
    }


def search(
    query: str, sido: str | None = None, sigungu: str | None = None, top_k: int = 10
) -> list[dict]:
    """Search for similar waste disposal items."""
    if model is None or embeddings is None or df is None:
        raise RuntimeError("Resources not loaded")

    indices = df.index.tolist()
    if sido:
        mask = df["시도명"] == sido
        if sigungu:
            mask &= df["시군구명"] == sigungu
        indices = df.index[mask].tolist()

    if not indices:
        return []

    similarities = (
        model.encode([query], normalize_embeddings=True) @ embeddings[indices].T
    )[0]

    top = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for i in top:
        row = df.iloc[indices[i]]
        results.append({
            "name": row["대형폐기물명"],
            "category": row["대형폐기물구분명"],
            "spec": row["대형폐기물규격"],
            "fee": int(row["수수료"]),
            "similarity": float(similarities[i]),
            "sido": row["시도명"],
            "sigungu": row["시군구명"],
        })
    return results
