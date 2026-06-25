# C3PO Main Skill

## Purpose
Comprehensive guide for working with the C3PO project.

## Overview
C3PO is an AI-powered educational tutoring platform with:
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **AI**: RAG-based chat with ChromaDB vector store
- **Real-time**: WebSocket support for live chat

## Quick Start
```bash
# Auto-start (from project root /workspace/project/c3po)
./setup.sh           # First-time setup
./start.sh           # Start services
./start.sh health    # Check status
```

## Services
| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| ChromaDB | 8001 | http://localhost:8001 |

## Skills Available
- `docker.md` - Docker and container management
- `backend-dev.md` - Backend development guide
- `frontend-dev.md` - Frontend development guide

## Environment Setup
1. Copy `.env.example` to `.env`
2. Add your `OPENAI_API_KEY`
3. Run `./setup.sh` or `docker-compose up -d`

## Common Operations

### Start Everything
```bash
cd /workspace/project/c3po
docker-compose up -d
```

### View Logs
```bash
cd /workspace/project/c3po
docker-compose logs -f
```

### Reset Database
```bash
cd /workspace/project/c3po
docker-compose down -v
docker-compose up -d
```

### Access Services
```bash
# Backend shell
docker exec -it c3po-backend sh

# Database
docker exec -it c3po-postgres psql -U c3po -d c3po_db
```

## Key Files
- `/workspace/project/c3po/docker-compose.yml` - Main compose file
- `/workspace/project/c3po/start.sh` - Quick start script
- `/workspace/project/c3po/setup.sh` - Setup script
- `/workspace/project/c3po/.env.example` - Environment template
- `/workspace/project/c3po/AGENTS.md` - Agent knowledge base

## Development Workflow
1. Make code changes in `backend/` or `frontend/`
2. Rebuild containers: `docker-compose up -d --build`
3. View logs: `docker-compose logs -f [service]`
4. Test the application at http://localhost:3000

## Troubleshooting
- **Services not starting**: Check `docker-compose logs`
- **Database errors**: Verify PostgreSQL is healthy
- **API errors**: Check backend logs and .env configuration
- **Frontend errors**: Clear `.next` cache and rebuild
