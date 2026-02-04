import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import SearchResponse
from app import search as search_module
from app import query_log

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

_app_logger = logging.getLogger("app")
_app_logger.setLevel(logging.INFO)
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
_app_logger.addHandler(_stream_handler)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    search_module.load_resources()
    query_log.setup()
    yield
    query_log.shutdown()


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


@app.get("/api/search", response_model=SearchResponse)
def search(
    query: str = Query(..., max_length=200),
    sido: str | None = Query(default=None, max_length=50),
    sigungu: str | None = Query(default=None, max_length=50),
):
    """Search for waste disposal items by similarity."""
    results = search_module.search(query=query, sido=sido, sigungu=sigungu)
    query_log.log_query(query, sido, sigungu, results)
    query_log.record_query(query, sido, sigungu)

    return JSONResponse(
        content={"results": results},
        headers={"Cache-Control": "no-store"},
    )
