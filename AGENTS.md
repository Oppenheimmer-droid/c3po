# C3PO Local Development with Docker Desktop

## Architecture Overview

This project uses a microservices architecture with Docker Compose for local development:

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Desktop                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │───▶│   Backend    │───▶│   PostgreSQL │  │
│  │  (Next.js)   │    │  (FastAPI)   │    │   (Database) │  │
│  │   Port 3000  │    │   Port 8000  │    │    Port 5432  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                            │                                 │
│                            ▼                                 │
│                     ┌──────────────┐                        │
│                     │   ChromaDB   │                        │
│                     │   Port 8001  │                        │
│                     └──────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services Configuration

### 1. PostgreSQL Database
- **Image**: `postgres:15-alpine`
- **Port**: `5432:5432`
- **Database**: `c3po_db`
- **User**: `c3po`
- **Password**: `c3po_secret` (change in production!)
- **Volume**: `postgres_data:/var/lib/postgresql/data`

### 2. Backend API (FastAPI)
- **Dockerfile**: `backend/Dockerfile`
- **Port**: `8000:8000`
- **Depends on**: PostgreSQL, ChromaDB
- **Environment Variables**:
  - `DATABASE_URL=postgresql://c3po:c3po_secret@postgres:5432/c3po_db`
  - `REDIS_URL=redis://redis:6379` (optional)
  - `CHROMA_HOST=chroma`
  - `CHROMA_PORT=8000`

### 3. ChromaDB Vector Store
- **Image**: `chromadb/chroma:latest`
- **Port**: `8001:8000`
- **Volume**: `chroma_data:/chroma/chroma`
- **Environment**:
  - `IS_PERSISTENT=TRUE`
  - `ANONYMIZED_TELEMETRY=FALSE`

### 4. Frontend (Next.js)
- **Dockerfile**: `frontend/Dockerfile`
- **Port**: `3000:3000`
- **Depends on**: Backend API
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL=http://backend:8000`
  - `NEXT_PUBLIC_WS_URL=ws://backend:8000`

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
POSTGRES_USER=c3po
POSTGRES_PASSWORD=c3po_secret
POSTGRES_DB=c3po_db

# Backend
DATABASE_URL=postgresql://c3po:c3po_secret@postgres:5432/c3po_db
SECRET_KEY=your-super-secret-key-change-in-production

# Optional: Redis (for Celery workers)
REDIS_URL=redis://redis:6379

# ChromaDB
CHROMA_HOST=chroma
CHROMA_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Deployment Workflow

### Development Mode

```bash
# Start services with hot-reload (volumes mounted)
docker-compose -f docker-compose.dev.yml up -d

# View specific service logs
docker-compose logs -f backend

# Restart a specific service
docker-compose restart backend
```

### Production Mode

```bash
# Build and start production containers
docker-compose up -d --build

# Check service health
docker-compose ps
```

## Troubleshooting

### View container logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Reset database
```bash
# Stop and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Rebuild from scratch
```bash
docker-compose down --rmi all -v
docker-compose up --build -d
```

## Ports Mapping

| Service    | Internal Port | External Port | URL                          |
|------------|---------------|---------------|------------------------------|
| Frontend   | 3000          | 3000          | http://localhost:3000       |
| Backend    | 8000          | 8000          | http://localhost:8000       |
| PostgreSQL | 5432          | 5432          | localhost:5432              |
| ChromaDB   | 8000          | 8001          | http://localhost:8001       |

## Health Checks

```bash
# Check all services status
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/collections  # ChromaDB
```

## Development Commands

```bash
# Access backend container shell
docker exec -it c3po-backend sh

# Access database
docker exec -it c3po-postgres psql -U c3po -d c3po_db

# Run migrations
docker exec -it c3po-backend alembic upgrade head

# Seed database
docker exec -it c3po-backend python -m app.scripts.seed_db
```

## File Structure

```
c3po/
├── docker-compose.yml          # Main compose file
├── docker-compose.dev.yml     # Development with hot-reload
├── docker-compose.prod.yml    # Production build
├── .env.example               # Environment template
├── AGENTS.md                  # This file
│
├── backend/
│   ├── Dockerfile             # Backend container
│   ├── requirements.txt      # Python dependencies
│   └── app/
│       ├── main.py           # FastAPI app
│       └── ...
│
├── frontend/
│   ├── Dockerfile            # Frontend container
│   ├── package.json          # Node dependencies
│   └── src/
│       └── ...
│
└── services/
    └── postgres/             # DB initialization scripts
```