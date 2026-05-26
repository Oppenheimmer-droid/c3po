# ReDrive Edu - Backend

AI-native contextual tutoring platform for education with RAG (Retrieval-Augmented Generation).

## Overview

ReDrive Edu is a SaaS platform that enables academies, professors, and students to interact with academic materials through AI-powered contextual tutoring, evaluations, and performance analytics.

### Key Features

- **Multi-tenant Architecture**: Complete isolation per academy/institution
- **RAG-powered Chat**: Contextual answers with cited sources from uploaded materials
- **Document Processing**: PDF, DOCX, TXT support with automatic chunking and embedding
- **Quiz Generation**: AI-generated assessments from course materials
- **Auto-grading**: Automatic evaluation and feedback
- **Analytics**: Student progress tracking and topic weakness identification

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend (Future)                          │
│                     React/Next.js / React Native                    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTP/REST
┌─────────────────────────────────▼───────────────────────────────────┐
│                         FastAPI Application                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Auth API  │  │  Documents  │  │    Chat    │  │  Eval API   │   │
│  │  (JWT/RBAC) │  │   Upload    │  │  (RAG)     │  │  (Quizzes)  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│         │                │                │                │         │
│  ┌──────▼────────────────▼────────────────▼────────────────▼──┐    │
│  │                      Services Layer                          │    │
│  │   AuthService  │  DocumentService  │  RAGService  │  EvalService │   │
│  └─────────────────┴──────────────────┴───────────────┴────────┘    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
   ┌────▼────┐              ┌─────▼─────┐            ┌─────▼─────┐
   │PostgreSQL│              │  Redis   │            │  ChromaDB │
   │(SQLAlchemy)│            │ (Cache/  │            │ (Vectors) │
   │         │              │  Broker) │            │           │
   └─────────┘              └──────────┘            └───────────┘
                                  │
                           ┌──────▼──────┐
                           │   Celery    │
                           │  Workers   │
                           └────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI + Pydantic v2 |
| Database | PostgreSQL + SQLAlchemy 2.x |
| Vector Store | ChromaDB |
| RAG Engine | LlamaIndex |
| LLM | OpenAI (gpt-4o-mini) |
| Workers | Celery + Redis |
| Auth | JWT with refresh tokens |
| Containerization | Docker + Docker Compose |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- OpenAI API key

### Local Development

1. **Clone and setup environment:**

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

2. **Start with Docker Compose:**

```bash
docker-compose up -d
```

3. **Access the API:**

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Manual Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Start services:**

```bash
# PostgreSQL
docker run -d --name redrive-postgres -p 5432:5432 \
  -e POSTGRES_DB=redrive_edu \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:16-alpine

# Redis
docker run -d --name redrive-redis -p 6379:6379 redis:7-alpine

# ChromaDB
docker run -d --name redrive-chroma -p 8000:8000 chromadb/chroma

# Run API
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register tenant + admin user |
| POST | `/api/v1/auth/login` | Login with credentials |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout user |
| GET | `/api/v1/auth/me` | Get current user info |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload document |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get document |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| GET | `/api/v1/documents/{id}/chunks` | Get document chunks |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/sessions` | Create chat session |
| GET | `/api/v1/chat/sessions` | List sessions |
| POST | `/api/v1/chat/sessions/{id}/messages` | Send message |
| GET | `/api/v1/chat/sessions/{id}/messages` | Get session messages |
| POST | `/api/v1/chat/query` | Simple RAG query |

### Evaluations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluations` | Create evaluation |
| GET | `/api/v1/evaluations` | List evaluations |
| GET | `/api/v1/evaluations/{id}/questions` | Get questions |
| POST | `/api/v1/evaluations/{id}/start` | Start attempt |
| POST | `/api/v1/evaluations/{id}/submit` | Submit answers |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql+asyncpg://... | PostgreSQL connection |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection |
| `OPENAI_API_KEY` | - | **Required** OpenAI API key |
| `OPENAI_MODEL` | gpt-4o-mini | LLM model |
| `OPENAI_EMBEDDING_MODEL` | text-embedding-3-small | Embedding model |
| `SECRET_KEY` | - | JWT signing key (min 32 chars) |
| `CHROMA_PERSIST_DIR` | ./chroma_data | ChromaDB storage |

## Project Structure

```
backend/
├── app/
│   ├── api/v1/           # API routers
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   └── evaluations.py
│   ├── core/             # Core functionality
│   │   ├── config.py     # Settings
│   │   ├── database.py  # DB connection
│   │   ├── security.py  # JWT/password utils
│   │   └── deps.py      # FastAPI dependencies
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── repositories/     # Data access
│   ├── rag/              # RAG pipeline
│   ├── workers/          # Celery tasks
│   └── tests/            # Test files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py -v
```

## Design Decisions

### Why ChromaDB?

- Simple to deploy and operate
- Good performance for single-tenant use cases
- Easy migration path to pgvector for multi-tenant at scale

### Why Celery?

- Mature task queue with Redis integration
- Built-in retry mechanisms and monitoring
- Horizontal scaling capability

### Why LlamaIndex?

- Excellent RAG abstractions
- Good integration with OpenAI
- Flexible retrieval strategies

### Multi-tenancy Strategy

- `tenant_id` column in all tables
- Middleware injects tenant context from JWT
- Separate ChromaDB collections per tenant
- Row-level security at repository layer

## Deployment

### Railway

```bash
# Add environment variables in Railway dashboard:
- DATABASE_URL
- REDIS_URL
- OPENAI_API_KEY
- SECRET_KEY

# Railway will auto-detect Dockerfile
```

### Fly.io

```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

## License

Proprietary - All rights reserved