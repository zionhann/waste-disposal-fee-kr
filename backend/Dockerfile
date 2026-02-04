FROM python:3.11-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

ENV HF_HOME=/build/.cache/huggingface \
    TORCH_HOME=/build/.cache/torch \
    PYTHONPATH=/build

# Isolated layer: model cache survives script/data changes
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('jhgan/ko-sroberta-multitask')"

COPY scripts/generate_embeddings.py scripts/generate_embeddings.py
COPY waste_disposal_fee.csv .
RUN python scripts/generate_embeddings.py

# App source last — changes most frequently
COPY app/ app/

# Runtime
FROM python:3.11-slim-bookworm

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appuser /build/app ./app
COPY --from=builder --chown=appuser:appuser /build/data ./data
COPY --from=builder --chown=appuser:appuser /build/.cache ./.cache
COPY --from=builder --chown=appuser:appuser /build/waste_disposal_fee.csv .

ENV PATH=/home/appuser/.local/bin:$PATH \
    HF_HOME=/app/.cache/huggingface \
    TORCH_HOME=/app/.cache/torch \
    PYTHONPATH=/app

RUN chown appuser:appuser /app && mkdir -p /app/logs && chown appuser:appuser /app/logs

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=5)"

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
