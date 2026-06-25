# C3PO - AI Educational Tutor Platform

A Next.js + FastAPI educational platform with AI-powered tutoring features, optimized for autonomous agent development.

## 🚀 Quick Start

```bash
# Auto-executable setup
./setup.sh

# Or manual start
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
docker-compose up -d

# Check status
./start.sh health
```

## 🌟 Features

- **AI-Powered Tutoring**: RAG-based chatbot with ChromaDB
- **Document Management**: Upload PDF, DOCX, TXT files
- **Evaluation System**: Track student progress
- **Multi-tenant**: Role-based access (Admin, Teacher, Student)
- **Real-time Chat**: WebSocket support
- **Analytics Dashboard**: Learning metrics

## 🏗️ Architecture

```
Frontend (Next.js) ──▶ Backend (FastAPI) ──▶ PostgreSQL
                            │
                            ▼
                     ChromaDB + Redis
```

## 📁 Project Structure

```
├── frontend/              # Next.js application
│   └── src/
│       ├── app/          # Pages
│       ├── components/   # UI components
│       └── services/     # API client
├── backend/              # FastAPI application
│   └── app/
│       ├── api/v1/      # API routes
│       ├── core/        # Config, security
│       ├── models/      # SQLAlchemy models
│       ├── schemas/     # Pydantic schemas
│       └── services/    # RAG, Chat, Auth
├── services/postgres/   # DB initialization
├── docker-compose.yml   # Container orchestration
├── setup.sh            # First-time setup
└── start.sh            # Quick start script
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `./setup.sh` | First-time setup |
| `./start.sh` | Start all services |
| `./start.sh health` | Health check |
| `./start.sh logs` | View logs |
| `./start.sh stop` | Stop services |
| `./start.sh reset` | Reset all data |

## 🌐 Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| ChromaDB | 8001 | http://localhost:8001 |

## 🤖 OpenHands Agents

This project includes skills for [OpenHands](https://docs.openhands.dev/) agents:

- `.openhands/skills/main.md` - Main skill
- `.openhands/skills/docker.md` - Docker management
- `.openhands/skills/backend-dev.md` - Backend development
- `.openhands/skills/frontend-dev.md` - Frontend development

## 📄 License

MIT License
