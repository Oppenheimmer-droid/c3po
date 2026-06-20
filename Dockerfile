# ============================================
# C3PO Backend - Railway Production
# ============================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc build-essential curl libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

COPY backend/app/ ./app/
RUN mkdir -p /app/uploads /app/chroma_data

# Railway inyecta PORT dinámicamente
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
