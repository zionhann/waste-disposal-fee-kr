from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import SearchRequest, SearchResponse, SearchResult
from app import search as search_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    search_module.load_resources()
    yield


app = FastAPI(title="Waste Disposal Search API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/locations")
def get_locations():
    """Get available locations for filtering."""
    return search_module.get_locations()


@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest):
    """Search for waste disposal items by similarity."""
    results = search_module.search(
        query=request.query,
        sido=request.sido,
        sigungu=request.sigungu,
    )
    return SearchResponse(
        results=[SearchResult(**r) for r in results]
    )
