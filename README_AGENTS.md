# C3PO Agents - AI Educational Tutor Platform

A Next.js + FastAPI educational platform with AI-powered tutoring features, optimized for autonomous agent development.

## 🚀 Quick Start (Auto-Executable)

```bash
# Clone and run
git clone <repo-url> c3po-agents
cd c3po-agents

# Option 1: One-command setup (if Docker is running)
./setup.sh

# Option 2: Manual start
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
docker-compose up -d

# Check status
./start.sh health
```

## 🌟 Features

- **AI-Powered Tutoring**: RAG-based chatbot with ChromaDB vector store
- **Document Management**: Upload and process PDF, DOCX, TXT files
- **Evaluation System**: Track student progress and learning outcomes
- **Multi-tenant Support**: Role-based access control (Admin, Teacher, Student)
- **Real-time Chat**: WebSocket support for live conversations
- **Analytics Dashboard**: Visualize learning metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     C3PO Architecture                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │───▶│   Backend    │───▶│   PostgreSQL │  │
│  │  (Next.js)   │    │  (FastAPI)   │    │   (Database) │  │
│  │   Port 3000  │    │   Port 8000  │    │    Port 5432  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                            │                                 │
│                            ▼                                 │
│                     ┌──────────────┐    ┌──────────────┐   │
│                     │   ChromaDB   │───▶│     Redis    │   │
│                     │   Port 8001  │    │   Port 6379   │   │
│                     └──────────────┘    └──────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
c3po/
├── .openhands/
│   └── skills/              # OpenHands agent skills
├── backend/
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic (RAG, Chat)
│   │   └── workers/        # Celery workers
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # Pages
│   │   ├── components/    # Reusable UI components
│   │   ├── lib/          # Store, utils
│   │   └── services/     # API client
│   └── Dockerfile
├── services/
│   └── postgres/         # DB initialization scripts
├── docker-compose.yml    # Main compose file
├── setup.sh             # First-time setup
├── start.sh             # Quick start/stop script
└── .env.example         # Environment template
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `./setup.sh` | First-time setup and installation |
| `./start.sh` | Start all services |
| `./start.sh health` | Check service health |
| `./start.sh logs` | View logs |
| `./start.sh stop` | Stop all services |
| `./start.sh reset` | Reset all data |
| `./start.sh restart` | Restart services |

## 🔐 Environment Variables

See `.env.example` for all configuration options. Required variables:

```bash
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
```

## 📦 Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| ChromaDB | 8001 | http://localhost:8001 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

## 🤖 OpenHands Integration

This project is designed to work with [OpenHands](https://docs.openhands.dev/) agents. 

### Available Skills

Skills for this project are stored in `.openhands/skills/`. To add custom skills:

1. Create a Markdown file in `.openhands/skills/`
2. Follow the OpenHands skill format
3. The agent will automatically load them

### Usage with OpenHands

```
# Start OpenHands with this project
openhands -i c3po

# Or use the OpenHands SDK
from openhands import Agent

agent = Agent(project_dir='/path/to/c3po')
agent.run('Deploy the application to production')
```

## 🧪 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Docker Development
```bash
# Start with hot-reload
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f backend

# Access container
docker exec -it c3po-backend sh
```

## 📚 Documentation

- [Frontend Documentation](./frontend/README.md)
- [Backend Documentation](./backend/README.md)
- [API Documentation](http://localhost:8000/docs)
- [OpenHands Documentation](https://docs.openhands.dev/)

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Next.js](https://nextjs.org/)
- AI features by [OpenAI](https://openai.com/)
- Vector search by [ChromaDB](https://www.trychroma.com/)
