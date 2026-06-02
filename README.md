# C3PO - AI Educational Tutor Platform

A Next.js + FastAPI educational platform with AI-powered tutoring features.

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Deployment**: Vercel (frontend), Railway (backend)

## Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/      # Pages (dashboard, chat, documents, evaluations)
│   │   ├── components/  # Reusable components
│   │   ├── lib/      # Store, utils, API client
│   │   └── services/ # API service modules
├── backend/          # FastAPI application
│   └── app/
│       ├── api/v1/   # API routes
│       ├── core/     # Config, security, database
│       ├── models/   # SQLAlchemy models
│       ├── schemas/  # Pydantic schemas
│       └── services/ # Business logic
└── vercel.json       # Vercel config
```

## Environment Variables

See `.env.example` for required variables.

## Deployment

- **Frontend**: Push to main → Vercel auto-deploys
- **Backend**: Railway auto-deploys from Dockerfile
