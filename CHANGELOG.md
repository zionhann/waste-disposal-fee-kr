# Changelog

## 2026-02-03

### feat(deploy): migrate from AWS Lambda to OCI A1 (ARM64) with Gunicorn

- `backend/requirements.txt`: Swap Lambda adapter for production ASGI stack
  - Remove `mangum` (Lambda-specific ASGI adapter)
  - Add `gunicorn` (process manager) and `uvicorn[standard]` (ASGI worker)
- `backend/app/main.py`: Strip Lambda handler wiring
  - Remove `mangum` import and `handler = Mangum(...)` entry point
- `backend/Dockerfile`: Rewrite as multi-stage ARM64 build
  - Stage 1 (builder): install deps, download model, generate embeddings
  - Stage 2 (runtime): copy only artifacts, run as non-root `appuser`
  - Add `HEALTHCHECK`, `EXPOSE 8000`, and exec-form `CMD ["bash", "start.sh"]`
- `backend/start.sh`: Add production startup script
  - Dynamic worker count from CPU cores, clamped 2–8
  - Pre-start validation of data files and embeddings
  - `exec` replaces shell with Gunicorn for correct PID-1 signal handling
- `backend/docker-compose.yml`: Add local ARM64 testing configuration
- `backend/DEPLOYMENT.md`: Add end-to-end OCI A1 deployment guide
- `backend/MIGRATION_SUMMARY.md`: Document architecture delta and rollback plan

### chore(deploy): replace gunicorn + start.sh with `fastapi run`

- `backend/requirements.txt`: Remove `gunicorn` and `uvicorn[standard]` (both bundled by `fastapi[standard]`)
- `backend/Dockerfile`: Simplify runtime stage
  - Remove `COPY start.sh`
  - Drop `WORKERS` env var
  - Replace `CMD ["bash", "start.sh"]` with `CMD ["fastapi", "run", ...]`
- `backend/start.sh`: Delete — no longer needed
- `backend/docker-compose.yml`: Remove `WORKERS=4` from environment

### refactor(backend): drop scikit-learn and requests, fix stale docs

- `backend/requirements.txt`: Remove `scikit-learn` and `requests` (6 → 4 lines)
- `backend/scripts/generate_embeddings.py`: Pass `normalize_embeddings=True` to `model.encode()` so stored vectors are unit-length
- `backend/app/search.py`: Replace cosine-similarity with dot-product similarity
  - Delete `sklearn.metrics.pairwise.cosine_similarity` import
  - Add `normalize_embeddings=True` to query encoding
  - Replace `cosine_similarity(…)[0]` with `(query_embedding @ filtered_embeddings.T)[0]`
  - Fix stale comment `# Encode query using KR-SBERT` → `# Encode query`
- `backend/Dockerfile`: Swap HEALTHCHECK from `requests.get` to stdlib `urllib.request.urlopen`
- `backend/docker-compose.yml`: Same HEALTHCHECK swap as Dockerfile
- `backend/DEPLOYMENT.md`: Remove all gunicorn / `start.sh` / `WORKERS` references
  - Update Architecture Overview server line
  - Strip `-e WORKERS=…` flags from all `docker run` examples
  - Delete "Using Startup Script (Alternative)" subsection
  - Delete `grep gunicorn` verification step
  - Delete `WORKERS` row from env-var table
  - Delete "Worker Tuning" subsection
  - Delete "Slow Response Times" troubleshooting subsection
  - Delete "Tune Gunicorn Settings" and "Use tmpfs" optimisation subsections
- `backend/MIGRATION_SUMMARY.md`: Delete — migration is complete and recorded in git log

### fix(deploy): correct `fastapi run` CMD argument from import path to file path

- `backend/Dockerfile`: Fix CMD on line 78
  - Replace `app.main:app` (uvicorn module syntax) with `app/main.py` (file path expected by `fastapi run`)

### refactor(backend): minimise codebase and optimise Dockerfile layer order

- `backend/app/main.py`: Adopt idiomatic FastAPI patterns
  - Replace module-level `load_resources()` call with `lifespan` context manager
  - Remove manual `SearchResult` construction — `response_model` validates automatically
  - Fix CORS: drop invalid `allow_credentials=True`, narrow methods/headers to actual usage
- `backend/app/search.py`: Remove dead work from the hot path
  - Delete unnecessary `df.copy()` — filter now builds an index mask directly on the original frame
  - Move NaN cleanup (`fillna`) to one-time load; per-row `pd.notna` guards removed from search loop
  - Remove `logging.basicConfig()` — let uvicorn own the root logger
- `backend/Dockerfile`: Restructure for fewer layers and stable cache
  - Inline model download as `RUN python -c …` — isolates the ~500 MB layer so script/data edits don't invalidate it
  - Reorder COPY: requirements → model → script+csv → embeddings → app source (most-changed last)
  - Replace `RUN chown -R` with per-COPY `--chown=appuser:appuser` (one fewer layer)
  - Remove dead `PORT` env var and redundant `RUN mkdir -p data`
  - Upgrade base from `bullseye` to `bookworm` (current Debian)
- `backend/docker-compose.yml`: Strip everything already in Dockerfile
  - Remove duplicated `healthcheck`, all `environment` overrides, commented-out volumes, and deprecated `version` key
- `backend/scripts/download_model.py`: Delete — logic inlined into Dockerfile
- `backend/DEPLOYMENT.md`: Update troubleshooting grep pattern and script reference to match new layout

### refactor(frontend): externalise API base URL into Vite env file

- `frontend/.env`: Create with shared default `VITE_API_BASE=http://localhost:8000`
- `frontend/src/api.ts`: Replace hardcoded URL with `import.meta.env.VITE_API_BASE`

### refactor(api): switch POST /api/search to GET with query-string params

- `backend/app/main.py`: Replace POST route with GET; bind params via `Query()`
  - Remove `SearchRequest` import; add `Query` from `fastapi`
  - Change `@app.post` → `@app.get`; replace single `request: SearchRequest` arg with three `Query()` parameters
- `backend/app/models.py`: Delete `SearchRequest` class (sole consumer was the POST route)
- `frontend/src/api.ts`: Rewrite `searchItems` fetch from POST+JSON body to GET+`URLSearchParams`
  - Build params with `query` always set; conditionally append `sido` / `sigungu`
  - Remove `method`, `headers`, and `body` options — plain GET is the default
- `backend/DEPLOYMENT.md`: Rewrite curl smoke-test example from `POST` with `-d` payload to a single GET URL
- `PRD.md`: Update API spec section
  - Change `POST /api/search` → `GET /api/search`
  - Replace "Request Body" JSON block with a "Query Parameters" table (`query` required, `sido` / `sigungu` optional)

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
