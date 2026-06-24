# 🚀 Deploy to Railway + Vercel

This guide explains how to deploy C3PO to production using **Railway** (backend) and **Vercel** (frontend).

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (Vercel)                             │
│                  https://[project].vercel.app                     │
│                                                                     │
│  Next.js 14 → API Routes → /api/* → Vercel Environment Vars      │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Backend (Railway)                            │
│                  https://[project].up.railway.app                 │
│                                                                     │
│  FastAPI → PostgreSQL → Redis → ChromaDB                          │
└──────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- GitHub account with repository access
- [Railway](https://railway.app) account
- [Vercel](https://vercel.com) account
- [Groq API Key](https://console.groq.com) (for AI features)

---

## Option 1: Automatic Deployment (Recommended)

### Step 1: Push to `deploy` Branch

```bash
git checkout -b deploy
git push origin deploy
```

This triggers the `deploy-production.yml` GitHub Action workflow.

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Description | Where to Get |
|--------|-------------|--------------|
| `RAILWAY_TOKEN` | Railway API token | Railway Dashboard → Account → Tokens |
| `VERCEL_TOKEN` | Vercel API token | Vercel Dashboard → Settings → Tokens |
| `VERCEL_ORG_ID` | Vercel organization ID | Vercel Dashboard → Settings → General |
| `VERCEL_PROJECT_ID` | Vercel project ID | Vercel Dashboard → Project Settings |
| `NEXT_PUBLIC_API_URL` | Your Railway backend URL | After first Railway deployment |
| `NEXT_PUBLIC_APP_URL` | Your Vercel app URL | After first Vercel deployment |

### Step 3: Configure Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Set the **Root Directory** to `backend`
4. Add environment variables:

```bash
SECRET_KEY=your-secure-random-string-min-32-chars
GROQ_API_KEY=your-groq-api-key
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://*.vercel.app
```

5. Add a PostgreSQL database (Railway → Add Plugin → PostgreSQL)
6. Add Redis (Railway → Add Plugin → Redis)
7. Note your Railway app URL (e.g., `https://c3po-api.up.railway.app`)

### Step 4: Configure Vercel

1. Create a new Vercel project
2. Import the `c3po` repository
3. Set **Root Directory** to `frontend`
4. Add environment variables:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
NEXT_PUBLIC_APP_URL=https://your-project.vercel.app
NEXT_PUBLIC_WS_URL=wss://your-railway-app.up.railway.app
```

5. Deploy!

---

## Option 2: Manual Deployment

### Backend (Railway)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Init project
cd backend
railway init

# Add PostgreSQL
railway add postgres

# Add Redis
railway add redis

# Deploy
railway up
```

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

---

## Environment Variables Reference

### Backend (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (auto from Railway) |
| `DATABASE_URL_SYNC` | Yes | Sync database URL for migrations |
| `REDIS_URL` | Yes | Redis connection string (auto from Railway) |
| `SECRET_KEY` | Yes | JWT signing key (min 32 characters) |
| `GROQ_API_KEY` | Yes | Groq API key for AI |
| `GROQ_MOCK` | No | Set `true` for demo mode (no API key) |
| `ENVIRONMENT` | Yes | `production` |
| `DEBUG` | No | `false` in production |
| `CORS_ORIGINS` | Yes | Vercel domains, e.g., `https://*.vercel.app` |
| `CHROMA_HOST` | No | ChromaDB host (default: localhost) |
| `CHROMA_PORT` | No | ChromaDB port (default: 8000) |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Railway backend URL |
| `NEXT_PUBLIC_APP_URL` | Yes | Vercel frontend URL |
| `NEXT_PUBLIC_WS_URL` | No | WebSocket URL for real-time |

---

## GitHub Actions Workflows

### `deploy-production.yml`

Triggers on push to `deploy` branch. Deploys both backend and frontend.

### `deploy-vercel.yml`

Triggers on push to `main` when frontend files change.

### `deploy.yml`

Runs tests for backend and frontend on push to `main`.

---

## Troubleshooting

### Backend 502 Errors

1. Check Railway logs: `railway logs`
2. Verify `DATABASE_URL` is set
3. Ensure `GROQ_API_KEY` is valid
4. Check health endpoint: `https://your-app.railway.app/api/v1/health`

### Frontend CORS Errors

1. Verify `CORS_ORIGINS` includes Vercel domains
2. Check `NEXT_PUBLIC_API_URL` is correct
3. Check browser console for specific errors

### Database Connection Issues

1. Verify PostgreSQL is running in Railway
2. Check `DATABASE_URL` format (should be `postgresql+asyncpg://...`)
3. Check Railway networking settings

---

## Production Checklist

- [ ] Set `SECRET_KEY` to a secure random value
- [ ] Configure `GROQ_API_KEY`
- [ ] Set `CORS_ORIGINS` to production domain
- [ ] Enable PostgreSQL (not SQLite)
- [ ] Configure Redis
- [ ] Test authentication flow
- [ ] Test chat/RAG functionality
- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Set up monitoring/logging

---

## Local Development

For local development, use `docker-compose`:

```bash
docker-compose up -d
```

Then:
- Backend: http://localhost:8001
- Frontend: http://localhost:3000
- API Docs: http://localhost:8001/docs
