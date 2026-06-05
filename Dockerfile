FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg y PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
