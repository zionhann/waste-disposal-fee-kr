# Changelog

## 2026-01-19

### data: merge 용산구 waste fee data from external source

- `waste_disposal_fee.csv`: Merge entries from 용산구 external dataset
  - Net additions: 24 new rows after deduplication
  - 용산구 total entries: 367 → 391

### fix(docs): resolve documentation inconsistencies and cleanup

- `PRD.md`: Update text format to structured format with labels (`품목: <대형폐기물명> | 구분: <대형폐기물구분명>`), update result count from 5 to 10
- `POC.md`: Update text format documentation to match new structured format
- `backend/app/search.py`: Correct misleading comment from "KR-SBERT" to "Korean sentence embedding model"
- `backend/scripts/generate_embeddings.py`: Change text format to structured labels, fix comment to reflect new format

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
