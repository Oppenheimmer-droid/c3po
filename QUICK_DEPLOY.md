# 🚀 Deployment Quick Start

## Status: ✅ Ready for Deployment

Todos los archivos necesarios están configurados y listos para deploy en Railway (Backend) + Vercel (Frontend).

---

## 📋 Pasos Rápidos

### 1️⃣ Generar SECRET_KEY (una sola vez)

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copia el valor generado, lo necesitarás en Railway.

---

### 2️⃣ Deploy Backend en Railway

1. Ir a [Railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub**
3. Seleccionar repo `c3po`
4. Seleccionar rama `main`
5. **Root Directory:** `backend`

#### Configurar Infraestructura en Railway:
- **PostgreSQL:** Click **+ New** → **Database** → **PostgreSQL**
- **Redis:** Click **+ New** → **Database** → **Redis**

#### Variables de Entorno en Railway:
```env
SECRET_KEY=<paste-generated-key>
ENVIRONMENT=production
DEBUG=false
OPENAI_API_KEY=<your-key>

# Auto-populadas por Railway
DATABASE_URL=<auto>
REDIS_URL=<auto>

# Estos se configurarán después
CORS_ORIGINS=https://your-vercel-domain.vercel.app
CELERY_BROKER_URL=${REDIS_URL}/1
CELERY_RESULT_BACKEND=${REDIS_URL}/2
CHROMA_PERSIST_DIR=/app/chroma_data
API_HOST=0.0.0.0
API_PORT=8000
```

**Toma nota de la URL pública de Railway** (ej: `https://c3po-prod.railway.app`)

---

### 3️⃣ Deploy Frontend en Vercel

1. Ir a [Vercel](https://vercel.com)
2. **Add New** → **Project** → **Import Git Repository**
3. Seleccionar repo `c3po`
4. **Framework Preset:** Next.js
5. **Root Directory:** `frontend`
6. **Build Command:** `npm run build`
7. **Output Directory:** `.next`

#### Variables de Entorno en Vercel:
```env
NEXT_PUBLIC_API_URL=https://c3po-prod.railway.app
```

(Reemplaza con la URL real de Railway)

**Toma nota de la URL de Vercel** (ej: `https://c3po-frontend.vercel.app`)

---

### 4️⃣ Actualizar CORS en Railway

Vuelve a Railway y actualiza:
```env
CORS_ORIGINS=https://c3po-frontend.vercel.app
```

---

## ✅ Verificación

### Backend Health Check
```bash
curl https://c3po-prod.railway.app/health
```

### Frontend
Abre en el navegador: `https://c3po-frontend.vercel.app`

---

## 📁 Archivos de Configuración Creados

| Archivo | Propósito |
|---------|-----------|
| `DEPLOY_STEPS.md` | Guía completa de deployment (paso a paso) |
| `DEPLOYMENT_GUIDE.md` | Guía original del proyecto |
| `DEPLOY_STEPS.md` | Instrucciones detalladas |
| `railway.json` | Configuración de Railway |
| `vercel.json` | Configuración de Vercel |
| `backend/.env.railway` | Variables de entorno para Railway |
| `frontend/.env.vercel` | Variables de entorno para Vercel |
| `backend/.railwayignore` | Archivos a ignorar en Railway |
| `frontend/.vercelignore` | Archivos a ignorar en Vercel |
| `.gitignore` | Archivos a ignorar en Git |
| `.env.example` | Template de variables de entorno |
| `verify-deployment.sh` | Script de verificación local |
| `deployment-checklist.sh` | Checklist interactivo |
| `.github/workflows/verify-deployment.yml` | CI/CD pre-deployment |

---

## 🔗 Recursos Útiles

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Production](https://nextjs.org/docs/going-to-production)

---

## 🆘 Soporte

Si algo no funciona:

1. Revisa [DEPLOY_STEPS.md](DEPLOY_STEPS.md) sección "Solución de problemas"
2. Verifica logs en Railway Dashboard
3. Abre DevTools (F12) en el navegador para errores frontend
4. Verifica que todas las variables de entorno estén configuradas

---

## 📝 Notas Importantes

- ⚠️ **No** commits de `.env` files (ya están en `.gitignore`)
- ⚠️ Genera una `SECRET_KEY` diferente para cada ambiente
- ⚠️ Usa OpenAI API key válida antes de hacer requests
- ✅ Railway auto-configura SSL/TLS
- ✅ Vercel auto-configura SSL/TLS
- ✅ Las migraciones de DB se ejecutan automáticamente (`alembic upgrade head`)

---

**¡Estás listo para deploy! 🚀**
