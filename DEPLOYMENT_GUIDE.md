# 🚀 Guía de Despliegue: Railway + Vercel + GitHub Actions

Esta guía te lleva paso a paso a través del despliegue inicial de ReDrive Edu en Railway (backend) y Vercel (frontend) con CI/CD automático.

---

## 📋 Pre-requisitos

✅ Cuenta en [GitHub](https://github.com) (ya tienes acceso a este repo)
✅ Cuenta en [Railway](https://railway.app)
✅ Cuenta en [Vercel](https://vercel.com)
✅ API Key válida de [OpenAI](https://platform.openai.com/api-keys)

---

## FASE 1: Generar Secretos y Credenciales

### 1. Generar SECRET_KEY segura

**En terminal (tu máquina local o codespace):**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Ejemplo de salida:**
```
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

👉 **Guarda este valor: lo necesitarás para Railway**

### 2. Obtener OPENAI_API_KEY

1. Ve a https://platform.openai.com/api-keys
2. Crea una nueva API Key
3. Cópiala (aparece solo una vez)

👉 **Guarda este valor: lo necesitarás para Railway**

---

## FASE 2: Despliegue del Backend en Railway

### Paso 1: Crear Proyecto en Railway

1. Abre https://railway.app
2. **Inicia sesión** con tu cuenta GitHub
3. Haz clic en **"+ New Project"**
4. Selecciona **"Deploy from GitHub"**
5. Busca y selecciona `Oppenheimmer-droid/c3po`
6. Selecciona la rama **`main`**

✅ Railway detectará automáticamente el `backend/Dockerfile`

---

### Paso 2: Agregar Plugins de Base de Datos

En el proyecto de Railway, ve a **"Variables"** en el panel izquierdo.

#### 2a. Agregar PostgreSQL

1. Haz clic en **"+ Add Plugin"** (o **"+ New"** si es desde Variables)
2. Selecciona **PostgreSQL**
3. Railway crea automáticamente:
   - `DATABASE_URL` con credenciales
   - Base de datos predeterminada

✅ **Verifica que `DATABASE_URL` aparece en Variables**

#### 2b. Agregar Redis

1. Haz clic en **"+ Add Plugin"**
2. Selecciona **Redis**
3. Railway crea automáticamente:
   - `REDIS_URL` con credenciales

✅ **Verifica que `REDIS_URL` aparece en Variables**

---

### Paso 3: Configurar Variables de Entorno

En Railway, ve a **Variables** del proyecto:

**Haz clic en "Add Variable" e ingresa cada una:**

| Variable | Valor | Notas |
|----------|-------|-------|
| `ENVIRONMENT` | `production` | No cambiar |
| `DEBUG` | `false` | No cambiar |
| `SECRET_KEY` | *[tu valor generado en FASE 1]* | Pegue el hex generado |
| `OPENAI_API_KEY` | *[tu API key de OpenAI]* | Pegue la clave sk-... |
| `OPENAI_MODEL` | `gpt-4o-mini` | No cambiar |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | No cambiar |
| `CHROMA_PERSIST_DIR` | `/app/chroma_data` | No cambiar |
| `LOG_LEVEL` | `INFO` | No cambiar |
| `CORS_ORIGINS` | `["https://c3po.vercel.app"]` | ⚠️ Actualizar después con URL real |
| `API_V1_PREFIX` | `/api/v1` | No cambiar |

**Variables que Railway genera automáticamente (no las toques):**
- ✅ `DATABASE_URL` — PostgreSQL
- ✅ `REDIS_URL` — Redis

---

### Paso 4: Iniciar Deploy del Backend

1. Ve a **"Deployments"** en el panel izquierdo
2. Railway hace build automático del Dockerfile
3. Espera a ver ✅ **"Active"** en verde

**Obtén la URL del backend:**
1. Haz clic en el contenedor backend (arriba a la izquierda)
2. Copia la URL bajo **"Public URL"** (ej: `https://backend-prod-xxxx.railway.app`)

👉 **Guarda esta URL: la necesitarás para Vercel**

**Verifica que el backend está corriendo:**
```
GET https://backend-prod-xxxx.railway.app/health
```
Debe retornar: `{"status":"ok"}`

**Verifica Swagger UI:**
```
GET https://backend-prod-xxxx.railway.app/docs
```
Debe mostrar la interfaz Swagger

✅ **Si ves tanto `/health` como `/docs`, el backend está listo**

---

### Paso 5: Ejecutar Migraciones de BD

Railway ejecuta automáticamente las migraciones gracias a `railway.json`, pero puedes verificar:

1. Ve a **"Logs"** en Railway
2. Busca el mensaje: `"INFO: Running migrations..."`
3. Verifica que termina con: `"INFO: Done migrating"`

✅ **Si ves estos mensajes, las migraciones se ejecutaron correctamente**

---

## FASE 3: Despliegue del Frontend en Vercel

### Paso 1: Conectar Vercel a GitHub

1. Abre https://vercel.com
2. Inicia sesión con GitHub
3. Haz clic en **"Add New..."** → **"Project"**
4. Selecciona `Oppenheimmer-droid/c3po`

---

### Paso 2: Configurar Carpeta y Variables

En Vercel:

1. **Root Directory**: Selecciona `frontend`
2. **Framework**: Vercel auto-detecta "Next.js"
3. Haz clic en **"Environment Variables"**

**Agrega estas variables:**

| Variable | Valor |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | *[URL del backend de Railway: https://backend-prod-xxxx.railway.app]* |
| `NEXT_PUBLIC_APP_URL` | *[Vercel auto-genera después del deploy]* |

👉 Por ahora solo `NEXT_PUBLIC_API_URL` es crítica

---

### Paso 3: Deploy del Frontend

1. Haz clic en **"Deploy"**
2. Espera a que Vercel construya y despliegue (2-3 min)
3. Cuando esté listo, verás ✅ **"Production"**

**Obtén la URL del frontend:**
- Haz clic en "Visit" o copia la URL (ej: `https://c3po.vercel.app`)

👉 **Guarda esta URL**

**Verifica que el frontend carga:**
```
GET https://c3po.vercel.app
```
Debe mostrar la página de inicio

---

### Paso 4: Actualizar CORS en Railway

Ahora que tienes la URL de Vercel, actualiza `ALLOWED_ORIGINS` en Railway:

1. Ve a Railway → Variables del backend
2. Edita `CORS_ORIGINS`:
   ```json
   ["https://c3po.vercel.app"]
   ```
3. Guarda cambios

✅ **Railway reinicia automáticamente el backend**

---

## FASE 4: Verificar CI/CD

### GitHub Actions

1. Abre tu repo en GitHub: https://github.com/Oppenheimmer-droid/c3po
2. Ve a **"Actions"** (pestaña superior)
3. Deberías ver 3 workflows:
   - ✅ `test-backend.yml`
   - ✅ `test-frontend.yml`
   - ✅ `deploy.yml`

**Prueba el workflow:**

1. Haz un pequeño cambio (ej: agrega un comentario)
2. Commitea a rama `develop` y abre Pull Request
3. GitHub Actions corre tests automáticamente
4. Verás ✅ o ❌ en la PR

### Auto-Deploy en Push a Main

Cuando hagas merge a `main`:

1. **GitHub Actions** corre tests
2. Si pasan, **Railway** redeploya backend automáticamente
3. **Vercel** redeploya frontend automáticamente

---

## 🧪 Prueba End-to-End

### 1. Crear Usuario

```bash
curl -X POST "https://backend-prod-xxxx.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

**Debe retornar:** `{"id": "...", "email": "test@example.com", ...}`

### 2. Login

```bash
curl -X POST "https://backend-prod-xxxx.railway.app/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

**Debe retornar:** `{"access_token": "...", "token_type": "bearer"}`

### 3. Acceder al Frontend

Abre https://c3po.vercel.app en tu navegador y:
- [ ] La página carga sin errores
- [ ] Puedes ir a `/auth/login`
- [ ] Las llamadas API van a la URL correcta (abre DevTools → Network)

---

## ✅ Checklist de Verificación Final

**Backend (Railway):**
- [ ] Dockerfile detectado y construido
- [ ] PostgreSQL y Redis plugin activos
- [ ] Variables de entorno todas configuradas
- [ ] `GET /health` retorna 200 OK
- [ ] `/docs` (Swagger) accesible
- [ ] Migraciones ejecutadas
- [ ] Logs sin errores

**Frontend (Vercel):**
- [ ] Proyecto conectado a GitHub
- [ ] Carpeta raíz: `frontend`
- [ ] Variables de entorno configuradas
- [ ] Build completado exitosamente
- [ ] Sitio accesible en URL pública
- [ ] Conecta correctamente al backend

**CI/CD:**
- [ ] 3 workflows creados en `.github/workflows/`
- [ ] Tests corren en PRs
- [ ] Auto-deploy funciona en merge a `main`

**Funcionalidad:**
- [ ] Registro de usuario funciona
- [ ] Login retorna token JWT
- [ ] Frontend carga datos del backend

---

## 🆘 Troubleshooting

### Backend no inicia

**Síntoma:** Deploy rojo ❌ en Railway

**Solución:**
1. Ve a Railway → Logs
2. Busca el error (ej: `ImportError`, `KeyError`)
3. Verifica que todas las variables de entorno estén presentes
4. Comprueba que `DATABASE_URL` y `REDIS_URL` existen

### Frontend no conecta al backend

**Síntoma:** Errores CORS o requests a `undefined`

**Solución:**
1. Abre DevTools (F12) → Console
2. Verifica que `NEXT_PUBLIC_API_URL` está correcta
3. En Railway, asegúrate que `CORS_ORIGINS` incluya la URL de Vercel
4. Reinicia el backend en Railway

### Migraciones no ejecutadas

**Síntoma:** Errores de tabla no encontrada

**Solución:**
1. Ve a Railway → Logs
2. Busca `"alembic"` en los logs
3. Si no aparece, la migración no corrió
4. En Railway, ve a "Shell" y ejecuta manualmente:
   ```bash
   alembic upgrade head
   ```

### Tests fallan en GitHub Actions

**Síntoma:** Red ❌ en workflow

**Solución:**
1. Abre el workflow fallido en GitHub → Actions
2. Lee los logs detallados
3. Generalmente es porque:
   - Falta instalar una dependencia
   - Requiere una variable de entorno específica
   - El servicio de PostgreSQL/Redis no está disponible

---

## 📚 Documentación Relacionada

- [README_TECNICO.md](../README_TECNICO.md) — Guía técnica completa
- [ARCHITECTURE.md](../ARCHITECTURE.md) — Arquitectura del sistema
- [Railway Docs](https://docs.railway.app) — Documentación de Railway
- [Vercel Docs](https://vercel.com/docs) — Documentación de Vercel

---

## 🎉 ¡Listo!

Si llegaste aquí sin errores, **¡felicidades!** Tu aplicación está desplegada en producción con:

✅ Backend corriendo en Railway con BD gestionada  
✅ Frontend corriendo en Vercel con CDN global  
✅ CI/CD automático con GitHub Actions  
✅ Migraciones ejecutadas automáticamente  
✅ Health checks y monitoreo configurados  

---

*Última actualización: 2026-05-26*
