import numpy as np
import pandas as pd
import logging
import time
from sentence_transformers import SentenceTransformer
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = BASE_DIR / "waste_disposal_fee.csv"

MODEL_NAME = "jhgan/ko-sroberta-multitask"

model: SentenceTransformer | None = None
embeddings: np.ndarray | None = None
df: pd.DataFrame | None = None


def load_resources():
    """Load model, embeddings, and data at startup."""
    global model, embeddings, df

    start_time = time.time()
    logger.info(f"Loading resources from {BASE_DIR}...")

    try:
        # Load Korean sentence embedding model
        model = SentenceTransformer(MODEL_NAME)
        
        embeddings_path = DATA_DIR / "embeddings.npy"
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings not found at {embeddings_path}. Please run generate_embeddings.py first.")
        
        embeddings = np.load(embeddings_path)
        
        if not CSV_PATH.exists():
            raise FileNotFoundError(f"CSV data not found at {CSV_PATH}")
            
        # Using utf-8-sig to handle Korean characters and potential BOM
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

        # Validate embedding dimensions match model
        expected_dim = 768
        if embeddings.shape[1] != expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {expected_dim}, got {embeddings.shape[1]}. "
                "Please regenerate embeddings with: python scripts/generate_embeddings.py"
            )
        
        elapsed = time.time() - start_time
        logger.info(f"Resources loaded successfully in {elapsed:.2f} seconds. Items: {len(df)}")

    except Exception as e:
        logger.error(f"Failed to load resources: {str(e)}")
        raise


def get_locations() -> dict:
    """Get unique sido and sigungu values."""
    if df is None:
        return {"sido": [], "sigungu": {}}

    sido_list = df["시도명"].unique().tolist()
    sigungu_map = df.groupby("시도명")["시군구명"].unique().apply(list).to_dict()

    return {"sido": sorted(sido_list), "sigungu": sigungu_map}


def search(
    query: str, sido: str | None = None, sigungu: str | None = None, top_k: int = 10
) -> list[dict]:
    """Search for similar waste disposal items."""
    if model is None or embeddings is None or df is None:
        raise RuntimeError("Resources not loaded")

    # Filter data by location
    filtered_df = df.copy()
    filtered_indices = df.index.tolist()

    if sido:
        mask = filtered_df["시도명"] == sido
        if sigungu:
            mask &= filtered_df["시군구명"] == sigungu
        filtered_df = filtered_df[mask]
        filtered_indices = filtered_df.index.tolist()

    if len(filtered_indices) == 0:
        return []

    # Get embeddings for filtered items
    filtered_embeddings = embeddings[filtered_indices]

    # Encode query using KR-SBERT
    query_embedding = model.encode([query])

    # Calculate cosine similarity
    similarities = cosine_similarity(query_embedding, filtered_embeddings)[0]

    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        original_idx = filtered_indices[idx]
        row = df.iloc[original_idx]
        results.append(
            {
                "name": row["대형폐기물명"],
                "category": row["대형폐기물구분명"],
                "spec": (
                    row["대형폐기물규격"] if pd.notna(row["대형폐기물규격"]) else ""
                ),
                "fee": int(row["수수료"]) if pd.notna(row["수수료"]) else 0,
                "similarity": float(similarities[idx]),
                "sido": row["시도명"],
                "sigungu": row["시군구명"],
            }
        )

    return results
