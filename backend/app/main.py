import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import SearchResponse
from app import search as search_module

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "query_log.jsonl"
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    search_module.load_resources()
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", errors="replace")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error("Failed to configure query log file %s: %s", LOG_FILE, e)
    yield


app = FastAPI(title="Waste Disposal Search API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Waste Disposal API is running"}


@app.get("/api/locations")
def get_locations():
    """Get available locations for filtering."""
    return search_module.get_locations()


def log_query(query: str, sido: str | None, sigungu: str | None, result_count: int):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "sido": sido,
        "sigungu": sigungu,
        "result_count": result_count,
    }
    logger.info(json.dumps(record, ensure_ascii=False))


@app.get("/api/search", response_model=SearchResponse)
def search(
    query: str = Query(...),
    sido: str | None = Query(default=None),
    sigungu: str | None = Query(default=None),
):
    """Search for waste disposal items by similarity."""
    results = search_module.search(query=query, sido=sido, sigungu=sigungu)
    log_query(query, sido, sigungu, len(results))
    return JSONResponse(
        content={"results": results},
        headers={"Cache-Control": "no-store"},
    )
