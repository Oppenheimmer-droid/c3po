FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para psycopg2-binary
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ /app/backend/

WORKDIR /app/backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
