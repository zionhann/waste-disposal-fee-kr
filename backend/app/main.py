from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.models import SearchRequest, SearchResponse, SearchResult
from app import search as search_module

app = FastAPI(title="Waste Disposal Search API")

# Load resources at startup (outside handler for Lambda Warm Start)
search_module.load_resources()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Waste Disposal API is running"}


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


# AWS Lambda handler
handler = Mangum(app, lifespan="off")
