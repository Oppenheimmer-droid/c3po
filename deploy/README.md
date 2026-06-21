# Deploy Guide - C3PO (ReDrive Edu)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Vercel (Frontend)                       │
│                   https://c3po-lime.vercel.app              │
│                         Node 20                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Railway (Backend)                        │
│              https://c3po-production-0c24.up.railway.app     │
│                   FastAPI + PostgreSQL                       │
└─────────────────────────────────────────────────────────────┘
```

## Quick Deploy

### Backend (Railway)

1. **Connect GitHub repo** to Railway
2. **Set variables** in Railway dashboard:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=sk-...
   ENVIRONMENT=production
   ```
3. **Deploy** - Railway auto-detects FastAPI

### Frontend (Vercel)

1. **Connect GitHub repo** to Vercel
2. **Set root directory**: `frontend`
3. **Set environment variables**:
   ```
   NEXT_PUBLIC_API_URL=https://c3po-production-0c24.up.railway.app
   ```
4. **Deploy** - Vercel auto-detects Next.js

## Local Development

### Backend
```bash
cd backend
cp .env.example .env
# Edit .env with your values
docker-compose -f docker-compose.yml up
```

### Frontend
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## Docker Production Deploy

```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

## Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@demo.com | admin123 |
| Teacher | teacher@demo.com | teacher123 |
| Student | student0@demo.com | student123 |
