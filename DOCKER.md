# 🐳 C3PO Docker Setup

This directory contains Docker configuration for running the C3PO application locally or in production.

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Oppenheimmer-droid/c3po.git
cd c3po

# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

### 2. Start Services

```bash
# Using the management script (recommended)
./docker.sh start

# Or directly with docker compose
docker compose up -d
```

### 3. Access Services

After starting, services will be available at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js application |
| API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |
| ChromaDB | localhost:8000 | Vector store |

## 📖 Management Commands

```bash
# Start services
./docker.sh start

# Stop services
./docker.sh stop

# Restart services
./docker.sh restart

# View all logs
./docker.sh logs

# View API logs only
./docker.sh logs-api

# View frontend logs only
./docker.sh logs-frontend

# Check service status
./docker.sh status

# Open shell in API container
./docker.sh shell-api

# Build images
./docker.sh build

# Clean up (removes all containers and volumes)
./docker.sh clean
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Network                        │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Postgres  │  │    Redis    │  │      ChromaDB       │ │
│  │   :5432     │  │    :6379    │  │       :8000         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                              │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │      API (FastAPI)      │  │   Frontend (Next.js)    │  │
│  │       :8000             │  │       :3000             │  │
│  └─────────────────────────┘  └─────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────┐                                 │
│  │     Celery Worker      │ (optional, with --profile worker)
│  └─────────────────────────┘                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

Edit `.env` to configure:

```env
# Security
SECRET_KEY=your-super-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/c3po

# OpenAI (optional - mock mode is enabled by default)
OPENAI_API_KEY=sk-your-api-key
OPENAI_MOCK=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Using External Services

To use external PostgreSQL, Redis, or ChromaDB instead of containers:

1. Edit the `DATABASE_URL`, `REDIS_URL`, and `CHROMA_*` variables in `.env`
2. Remove those services from `docker-compose.yml`
3. Run `./docker.sh start`

## 🏭 Production Deployment

For production, use the production compose file:

```bash
# Set required environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/c3po"
export SECRET_KEY="your-production-secret-key"
export CORS_ORIGINS="https://your-domain.com"

# Start with production config
docker compose -f docker-compose.prod.yml up -d
```

## 🐛 Troubleshooting

### Port already in use

If you get port conflicts:

```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Or change ports in docker-compose.yml
```

### Database connection errors

```bash
# Check if postgres is healthy
docker compose ps postgres

# View postgres logs
docker compose logs postgres

# Reset database
docker compose down -v
docker compose up -d
```

### Frontend not loading

```bash
# Check if frontend built correctly
docker compose logs frontend

# Rebuild frontend
docker compose build frontend
docker compose up -d frontend
```

## 📝 File Structure

```
├── docker-compose.yml       # Development configuration
├── docker-compose.prod.yml  # Production configuration
├── Dockerfile.frontend      # Frontend multi-stage build
├── backend/
│   └── Dockerfile          # Backend multi-stage build
├── nginx.conf               # Production nginx config
├── .env.example             # Environment template
├── .env                     # Your environment (git ignored)
└── docker.sh                # Management script
```

## 🔒 Security Notes

- Never commit `.env` to version control
- Use strong `SECRET_KEY` in production
- Keep Docker images updated
- Review CORS origins for production