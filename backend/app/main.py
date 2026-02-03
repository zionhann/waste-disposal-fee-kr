from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import SearchResponse
from app import search as search_module


@asynccontextmanager
async def lifespan(_app: FastAPI):
    search_module.load_resources()
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


@app.get("/api/search", response_model=SearchResponse)
def search(
    query: str = Query(...),
    sido: str | None = Query(default=None),
    sigungu: str | None = Query(default=None),
):
    """Search for waste disposal items by similarity."""
    return {"results": search_module.search(
        query=query, sido=sido, sigungu=sigungu,
    )}
