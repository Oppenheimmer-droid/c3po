# C3PO Production Deployment Guide

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Vercel (Frontend)                       │
│                   https://your-project.vercel.app            │
│                         Node 20                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Railway (Backend)                        │
│              https://your-backend.up.railway.app             │
│                   FastAPI + PostgreSQL                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment Options

### Option 1: Cloud Deploy (Railway + Vercel)

#### Backend → Railway

1. Connect GitHub repo to Railway
2. Set root directory: `backend`
3. Use `Dockerfile.prod` (auto-detected)
4. Set environment variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Generate strong random key |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `https://*.vercel.app,https://your-domain.com` |

5. Railway will auto-detect and deploy

#### Frontend → Vercel

1. Connect GitHub repo to Vercel
2. Set root directory: `frontend`
3. Set environment variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your Railway backend URL |
| `NEXT_PUBLIC_WS_URL` | Your Railway WebSocket URL |
| `NEXT_TELEMETRY_DISABLED` | `1` |

4. Deploy - Vercel auto-detects Next.js

---

### Option 2: Docker Production (Self-Hosted)

```bash
# Copy production environment
cp .env.production.example .env.production
# Edit .env.production with real values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# With Nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

---

### Option 3: Docker Compose (Local Production Test)

```bash
# Development with production-like settings
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📋 Required Environment Variables

### Backend (Railway)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DATABASE_URL_SYNC=postgresql+psycopg2://user:pass@host:5432/db

# Security
SECRET_KEY=your-very-long-random-secret-key-min-32-chars

# AI
OPENAI_API_KEY=sk-your-openai-key

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=https://yourdomain.com,https://*.vercel.app
```

### Frontend (Vercel)

```bash
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
NEXT_PUBLIC_WS_URL=wss://your-railway-backend.up.railway.app
NEXT_TELEMETRY_DISABLED=1
```

## 🌐 DNS Configuration

If using custom domain:

1. **Vercel**: Add domain in project settings
2. **Railway**: Add custom domain in networking tab
3. Update `CORS_ORIGINS` with your domain

## 🔒 Security Checklist

- [ ] Generate strong `SECRET_KEY`
- [ ] Use production database (not local)
- [ ] Enable `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` with allowed domains
- [ ] Use HTTPS everywhere
- [ ] Set up SSL certificates
- [ ] Configure rate limiting

## 📊 Health Checks

| Service | Endpoint |
|---------|----------|
| Backend | `GET /health` |
| Frontend | `GET /` |
| ChromaDB | `GET /api/v1/collections` |

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Verify DATABASE_URL format
# Should be: postgresql+asyncpg://...
```

### CORS errors
- Verify `CORS_ORIGINS` includes your frontend domain
- Check `NEXT_PUBLIC_API_URL` matches backend URL

### Database connection failed
- Verify `DATABASE_URL` is correct
- Check database is accessible from deployment

## 📝 Credentials (Demo Users)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@demo.com | admin123 |
| Teacher | teacher@demo.com | teacher123 |
| Student | student0@demo.com | student123 |

⚠️ **Change these in production!**

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
