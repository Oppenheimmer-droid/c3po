FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for chromadb
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run simple file server for frontend
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
