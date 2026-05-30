FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar TODO el backend
COPY backend /app/backend

# Añadir backend al PYTHONPATH
ENV PYTHONPATH="/app/backend"

# Entrar al directorio backend
WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
