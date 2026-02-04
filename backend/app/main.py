import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import SearchResponse
from app import search as search_module

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "query.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

_app_logger = logging.getLogger("app")
_app_logger.setLevel(logging.INFO)
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
_app_logger.addHandler(_stream_handler)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    search_module.load_resources()
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", errors="replace")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
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


def log_query(query: str, sido: str | None, sigungu: str | None, results: list[dict]):
    top_names = ", ".join(r["name"] for r in results[:5])
    logger.info(
        'query="%s" sido=%s sigungu=%s results=[%s]',
        query,
        sido or "-",
        sigungu or "-",
        top_names,
    )


@app.get("/api/search", response_model=SearchResponse)
def search(
    query: str = Query(...),
    sido: str | None = Query(default=None),
    sigungu: str | None = Query(default=None),
):
    """Search for waste disposal items by similarity."""
    results = search_module.search(query=query, sido=sido, sigungu=sigungu)
    log_query(query, sido, sigungu, results)
    return JSONResponse(
        content={"results": results},
        headers={"Cache-Control": "no-store"},
    )
