# 🚀 Guía de Deployment: Railway + Vercel

## 📋 Tabla de Contenidos
1. [Preparación](#preparación)
2. [Deployment en Railway (Backend)](#deployment-en-railway-backend)
3. [Deployment en Vercel (Frontend)](#deployment-en-vercel-frontend)
4. [Configuración Final](#configuración-final)
5. [Verificación](#verificación)

---

## Preparación

### 1. Generar SECRET_KEY

En tu terminal local:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Guarda el valor generado, lo usarás en Railway.

### 2. Clonar el repositorio localmente

```bash
git clone https://github.com/Oppenheimmer-droid/c3po.git
cd c3po
```

---

## Deployment en Railway (Backend)

### Paso 1: Crear proyecto en Railway

1. Ve a [Railway.app](https://railway.app)
2. Haz click en **"New Project"**
3. Selecciona **"Deploy from GitHub"**
4. Autoriza Railway con tu cuenta de GitHub
5. Selecciona el repositorio `c3po`
6. Selecciona la rama `main`
7. Configura el directorio raíz como `backend`

### Paso 2: Crear servicios de infraestructura

En el dashboard de Railway:

#### PostgreSQL Database
1. Click en **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway creará automáticamente:
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `DATABASE_URL`

#### Redis
1. Click en **"+ New"** → **"Database"** → **"Redis"**
2. Railway creará automáticamente:
   - `REDIS_URL`

### Paso 3: Configurar variables de entorno

En el dashboard, ve a **"Variables"** y añade:

```env
# Copiar estos valores de PostgreSQL y Redis (se crean automáticamente)
DATABASE_URL=postgresql+psycopg2://[user]:[password]@[host]:[port]/[db]
REDIS_URL=redis://[user]:[password]@[host]:[port]

# Configuración de la aplicación
SECRET_KEY=<paste-the-secret-key-generated-earlier>
ENVIRONMENT=production
DEBUG=false
OPENAI_API_KEY=<your-openai-api-key>

# CORS (se actualizará después del deploy de Vercel)
CORS_ORIGINS=https://your-vercel-domain.vercel.app
ALLOW_CREDENTIALS=true

# Celery
CELERY_BROKER_URL=$REDIS_URL/1
CELERY_RESULT_BACKEND=$REDIS_URL/2

# ChromaDB
CHROMA_PERSIST_DIR=/app/chroma_data

# API Host
API_HOST=0.0.0.0
API_PORT=8000
```

### Paso 4: Configurar Deployment

En **"Deployment"** → **"Settings"**:

```json
{
  "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000",
  "healthchecks": {
    "readiness": {
      "command": "curl --fail http://localhost:8000/health || exit 1"
    },
    "liveness": {
      "command": "curl --fail http://localhost:8000/health || exit 1"
    }
  }
}
```

### Paso 5: Hacer deploy

Railway detectará automáticamente el `Dockerfile` en `/backend` y hará el deploy. Monitorea en la pestaña **"Deployments"**.

**Nota:** Toma nota de la URL pública que Railway asigna (ej: `https://c3po-prod.railway.app`)

---

## Deployment en Vercel (Frontend)

### Paso 1: Crear proyecto en Vercel

1. Ve a [Vercel](https://vercel.com)
2. Haz click en **"New Project"**
3. Importa el repositorio `c3po` desde GitHub
4. En **"Project Settings"**:
   - **Framework Preset:** Next.js
   - **Root Directory:** `./frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

### Paso 2: Configurar variables de entorno

En **"Settings"** → **"Environment Variables"**, añade:

```env
NEXT_PUBLIC_API_URL=https://c3po-prod.railway.app
```

(Reemplaza con la URL real de Railway)

### Paso 3: Hacer deploy

Vercel detectará `next.config.js` y hará el deploy automáticamente.

**Nota:** Toma nota de la URL de Vercel (ej: `https://c3po-frontend.vercel.app`)

---

## Configuración Final

### Actualizar CORS en Railway

Ahora que tienes la URL de Vercel, vuelve a Railway y actualiza:

```env
CORS_ORIGINS=https://c3po-frontend.vercel.app
```

---

## Verificación

### 1. Verificar Backend en Railway

```bash
curl https://c3po-prod.railway.app/health
```

Deberías recibir: `{"status": "ok"}`

### 2. Verificar Frontend en Vercel

Abre: `https://c3po-frontend.vercel.app`

Deberías ver la página de login.

### 3. Verificar conectividad

En el frontend, intenta:
1. Registrarte
2. Hacer login
3. Acceder a un documento

Si todo funciona, ¡estás listo! 🎉

---

## 📱 Próximas pasos

- Configurar CI/CD en GitHub Actions para deploys automáticos
- Configurar monitoring y logging
- Configurar backups automáticos de PostgreSQL
- Configurar SSL/TLS (incluido en Railway)

---

## 🆘 Solución de problemas

### Backend no levanta
- Verifica logs en Railway: **"Logs"** → busca errores
- Asegúrate de que PostgreSQL y Redis estén conectados
- Verifica que `alembic upgrade head` se ejecute correctamente

### Frontend no conecta al backend
- Verifica que `NEXT_PUBLIC_API_URL` esté correctamente configurada
- Verifica que CORS_ORIGINS en Railway incluya la URL de Vercel
- Abre DevTools (F12) → Network para ver errores

### Base de datos vacía
- Ejecuta el script seed:
  ```bash
  docker exec <backend-container> python scripts/seed.py
  ```

