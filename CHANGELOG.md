# Changelog

## 2026-01-16

### feat: implement initial waste disposal search system

- `PRD.md`: Create product requirements document with system architecture, API specs, and data pipeline
- `backend/requirements.txt`: Define Python dependencies (FastAPI, sentence-transformers, numpy, pandas)
- `backend/app/__init__.py`: Initialize app module
- `backend/app/models.py`: Define Pydantic models for search request/response
- `backend/app/search.py`: Implement semantic search with ko-sbert-sts embeddings and cosine similarity
- `backend/app/main.py`: Create FastAPI app with CORS and search/locations endpoints
- `backend/scripts/generate_embeddings.py`: Script to preprocess data and generate .npy embeddings
- `frontend/src/types.ts`: Define TypeScript types for API responses
- `frontend/src/api.ts`: Implement API client for search and locations
- `frontend/src/App.tsx`: Build search UI with sido/sigungu filters and results display
- `frontend/src/App.css`: Style search form and result cards
- `frontend/src/index.css`: Set global styles with light theme
