# C3PO Agents Branch

This is the **agents** branch of C3PO, optimized for autonomous AI agent development using [OpenHands](https://docs.openhands.dev/).

## 🚀 Quick Start

```bash
# One-command setup
./setup.sh

# Or manual start
cp .env.example .env
# Add your OPENAI_API_KEY to .env
docker-compose up -d
```

## 🤖 What Makes This Branch Special?

### OpenHands Skills
Skills are markdown files that tell OpenHands how to work with this project:

```
.openhands/skills/
├── main.md           # Main project guide
├── docker.md         # Docker commands
├── backend-dev.md    # Backend development
└── frontend-dev.md   # Frontend development
```

### Auto-Executable Scripts
- `setup.sh` - First-time setup
- `start.sh` - Start/stop/health/restart/logs/reset

### Agent-Ready
- Clear environment variables
- Health checks for all services
- Structured for autonomous operations

## 📦 Services

| Service | Port | Health Check |
|---------|------|--------------|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000/health |
| ChromaDB | 8001 | http://localhost:8001/api/v1/collections |
| PostgreSQL | 5432 | pg_isready |
| Redis | 6379 | redis-cli ping |

## 🔧 Common Agent Commands

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f backend

# Reset database
docker-compose down -v && docker-compose up -d

# Health check
./start.sh health
```

## 📚 Documentation

- [Main README](README.md)
- [Agents README](README_AGENTS.md)
- [AGENTS.md](AGENTS.md) - Agent knowledge base
- [Skills](.openhands/skills/)

## 🏷️ Version

This release: **v1.0.0-agents**

See [CHANGELOG.md](CHANGELOG.md) for full history.
