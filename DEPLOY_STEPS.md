# 🚀 Deployment Guide - C3PO Platform

This guide provides step-by-step instructions for deploying C3PO to production.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vercel)                        │
│                    https://your-app.vercel.app                   │
│                                                                   │
│  Next.js 14 → API Routes → /api/* → Vercel Edge Rewrites       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend (Railway)                          │
│                    https://api.c3po-app.up.railway.app          │
│                                                                   │
│  FastAPI → PostgreSQL → Redis → ChromaDB                         │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- GitHub account
- Vercel account (for frontend)
- Railway account (for backend)
- Groq API key (for AI) - Get at https://console.groq.com
- PostgreSQL database (Railway provides)

---

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to [Railway](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select the `c3po` repository
4. Select the `backend` directory as the root

### 1.2 Configure Environment Variables

In Railway project settings, add these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | (from Railway PostgreSQL) | Auto-configured |
| `SECRET_KEY` | `your-secure-random-string` | Min 32 characters |
| `GROQ_API_KEY` | `gsk_...` | From Groq console |
| `CORS_ORIGINS` | `https://*.vercel.app` | Vercel domains |
| `ENVIRONMENT` | `production` | |
| `DEBUG` | `false` | |

### 1.3 Deploy

Railway will automatically detect the `railway.toml` and deploy.

**Wait for deployment to complete**, then note your backend URL:
```
https://c3po-production-xxx.up.railway.app
```

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Connect to Vercel

1. Go to [Vercel](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository `c3po`
4. Set the root directory to `frontend`

### 2.2 Configure Environment Variables

In Vercel project settings, add:

| Variable | Value |
|---------|-------|
| `NEXT_PUBLIC_API_URL` | `https://c3po-production-xxx.up.railway.app` |
| `NEXT_PUBLIC_APP_URL` | `https://your-app.vercel.app` |

### 2.3 Deploy

Click "Deploy" - Vercel will automatically use the `vercel.json` configuration.

---

## Step 3: Verify Integration

### 3.1 Test Backend

```bash
curl https://c3po-production-xxx.up.railway.app/api/v1/health
# Expected: {"status": "ok"}
```

### 3.2 Test Frontend

Visit your Vercel URL. The frontend should connect to the Railway backend.

---

## Step 4: Configure Custom Domain (Optional)

### Vercel Domain
1. Go to Project Settings → Domains
2. Add your custom domain (e.g., `app.example.com`)
3. Update DNS records as instructed

### Railway Domain
1. Go to Settings → Networking → Public Networking
2. Your backend will be accessible via Railway-provided URL
3. Update `NEXT_PUBLIC_API_URL` in Vercel if domain changes

---

## Troubleshooting

### Backend 502 Errors
- Check Railway logs for startup errors
- Verify `DATABASE_URL` is set correctly
- Ensure `GROQ_API_KEY` is valid

### Frontend API Errors
- Verify `NEXT_PUBLIC_API_URL` points to Railway URL
- Check browser console for CORS errors
- Ensure Railway backend is running

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 on Railway | Check `railway.toml` and logs |
| CORS errors | Verify `CORS_ORIGINS` includes Vercel domains |
| API timeout | Increase Railway timeout or optimize queries |
| Build fails | Check `vercel.json` build command |

---

## Automation with GitHub Actions

The repository includes GitHub Actions workflows:

- `.github/workflows/deploy.yml` - Deploy backend
- `.github/workflows/deploy-vercel.yml` - Deploy frontend
- `.github/workflows/test-backend.yml` - Run tests
- `.github/workflows/verify-deployment.yml` - Pre-deployment checks

### Required Secrets

In GitHub repository Settings → Secrets:

| Secret | Description |
|--------|-------------|
| `VERCEL_TOKEN` | Vercel API token |
| `VERCEL_ORG_ID` | Vercel organization ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |

---

## Production Checklist

- [ ] Set `SECRET_KEY` to secure random value
- [ ] Configure `GROQ_API_KEY` (or OpenAI alternative)
- [ ] Set `CORS_ORIGINS` to production domain
- [ ] Enable PostgreSQL (not SQLite)
- [ ] Configure Redis for production
- [ ] Set up monitoring/logging
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Test authentication flow
- [ ] Test file uploads
- [ ] Test RAG/chat functionality
