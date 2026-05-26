# 📚 Documentación Técnica - ReDrive Edu

> **Nota**: Esta guía está destinada a administradores de sistemas y desarrolladores. Para instrucciones simplificadas para usuarios finales, consulta `GUIA_USUARIO_FINAL.md`.

---

## 📋 Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Variables de Entorno](#variables-de-entorno)
3. [Despliegue en Producción](#despliegue-en-producción)
4. [Comandos de Administración](#comandos-de-administración)
5. [Migraciones de Base de Datos](#migraciones-de-base-de-datos)
6. [Backups y Restauración](#backups-y-restauración)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Seguridad](#seguridad)
9. [Solución de Problemas Avanzados](#solución-de-problemas-avanzados)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                               │
│                    (Navegador / App)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                    LOAD BALANCER                             │
│                (Railway / Vercel / Nginx)                    │
└───────────┬─────────────────────────────────┬───────────────┘
            │                                 │
            ▼                                 ▼
┌───────────────────┐               ┌───────────────────┐
│   FRONTEND         │               │   BACKEND         │
│   (Next.js)        │               │   (FastAPI)       │
│   Vercel           │               │   Railway         │
│   Port: 3000       │               │   Port: 8000      │
└───────────────────┘               └─────────┬─────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
           ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
           │ PostgreSQL  │          │    Redis    │          │  ChromaDB   │
           │  (Datos)    │          │   (Cache)   │          │ (Vectores)  │
           │ Port: 5432  │          │ Port: 6379  │          │ Port: 8000  │
           └─────────────┘          └─────────────┘          └─────────────┘
```

### Componentes

| Componente | Tecnología | Descripción |
|------------|------------|-------------|
| Frontend | Next.js 14 | Interfaz de usuario, SSR/SSG |
| Backend | FastAPI + Pydantic | API REST, validación, auth |
| Database | PostgreSQL 16 | Datos relacionales (usuarios, docs, etc.) |
| Cache | Redis 7 | Sesiones, tokens, cache de queries |
| Vector DB | ChromaDB | Embeddings y búsqueda semántica |
| Workers | Celery | Tareas asíncronas (OCR, embeddings) |
| LLM | OpenAI GPT-4o-mini | Generación de lenguaje natural |

---

## 🔐 Variables de Entorno

### Backend (.env)

```env
# ====================
# CONFIGURACIÓN BÁSICA
# ====================

# Entorno (development / production)
ENVIRONMENT=production

# Clave secreta para JWT (MINIMO 32 caracteres, aleatoria)
SECRET_KEY=tu-clave-secreta-minimo-32-caracteres-aqui

# Modo debug (solo development)
DEBUG=false

# ====================
# BASE DE DATOS
# ====================

# PostgreSQL ( Railway proporciona esto automáticamente )
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# ====================
# REDIS
# ====================

# Redis ( para cache y Celery )
REDIS_URL=redis://user:password@host:port/0

# ====================
# OPENAI
# ====================

# Clave API de OpenAI (OBLIGATORIO)
OPENAI_API_KEY=sk-...

# Modelo LLM (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Modelo embeddings (default: text-embedding-3-small)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ====================
# CHROMADB
# ====================

# Directorio persistente para ChromaDB
CHROMA_PERSIST_DIR=/app/chroma_data

# ====================
# CORS (solo si necesitas другой dominio)
# ====================

ALLOWED_ORIGINS=http://localhost:3000,https://tu-dominio.com
```

### Frontend (.env.local)

```env
# URL del backend ( Railway proporciona la URL automáticamente )
NEXT_PUBLIC_API_URL=https://tu-backend.railway.app

# URL de la aplicación
NEXT_PUBLIC_APP_URL=https://tu-frontend.vercel.app
```

---

## 🚀 Despliegue en Producción

### Opción 1: Railway (Recomendado)

**Ventajas**: Despliegue automático, bases de datos gestionadas, SSL incluido.

#### Backend

1. **Crear proyecto en Railway**
   - Ve a https://railway.app
   - Crea una cuenta / inicia sesión
   - New Project → Deploy from GitHub
   - Selecciona el repositorio

2. **Configurar variables**
   - Variables → Add Variable
   - Añade todas las variables de `.env`
   - IMPORTANTE: `DATABASE_URL`, `REDIS_URL` se crean automáticamente con los plugins

3. **Desplegar**
   - Railway detecta el Dockerfile automáticamente
   - Hace build y deploy
   - Obtén la URL del servicio (ej: `https://backend-xxx.railway.app`)

#### Frontend (Vercel)

1. **Conectar Vercel**
   - Ve a https://vercel.com
   - Importar proyecto desde GitHub
   - Selecciona la carpeta `frontend`

2. **Configurar dominio**
   - Environment Variables
   - `NEXT_PUBLIC_API_URL` = URL del backend en Railway

3. **Desplegar**
   - Vercel hace build y deploy automáticamente

#### Plugins de Railway (opcionales)

```bash
# Añadir PostgreSQL
railway add postgresql

# Añadir Redis
railway add redis

# Ver logs
railway logs
```

---

### Opción 2: Fly.io

#### Backend

```bash
# Instalar flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch
fly launch

# Establecer secrets
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set SECRET_KEY=tu-clave-secreta

# Deploy
fly deploy
```

#### Frontend

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

---

### Opción 3: VPS/Servidor Propio

#### Requisitos
- Ubuntu 22.04 LTS
- 2GB RAM mínimo
- Docker y Docker Compose instalados

#### Instalación

```bash
# Clonar repositorio
git clone https://github.com/Oppenheimmer-droid/c3po.git
cd c3po

# Configurar producción
cp backend/.env.example backend/.env
nano backend/.env  # Editar con tus valores

# Docker Compose para producción
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🛠️ Comandos de Administración

### Docker Compose (Desarrollo)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (BORRA DATOS)
docker-compose down -v

# Reiniciar un servicio
docker-compose restart backend

# Rebuild sin cache
docker-compose build --no-cache
```

### Docker Compose (Producción)

```bash
# Iniciar con restart policy
docker-compose -f docker-compose.prod.yml up -d

# Escalar servicios
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# Backup antes de actualizar
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres redrive_edu > backup_$(date +%Y%m%d).sql
```

---

## 🗄️ Migraciones de Base de Datos

### Con Alembic (Desarrollo)

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Ver estado de migraciones
alembic current
alembic history

# Hacer downgrade
alembic downgrade -1
```

### En Producción (Railway)

```bash
# Ejecutar migraciones después de deploy
railway run alembic upgrade head
```

---

## 💾 Backups y Restauración

### Backup PostgreSQL

```bash
# Backup local
docker-compose exec -T postgres pg_dump -U postgres redrive_edu > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup remoto (desde servidor)
pg_dump -h hostname -U username -d database > backup.sql

# Backup con compresión
docker-compose exec -T postgres pg_dump -U postgres redrive_edu | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restaurar PostgreSQL

```bash
# Restaurar desde backup
docker-compose exec -T postgres psql -U postgres -d redrive_edu < backup.sql

# Restaurar desde gzip
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres -d redrive_edu
```

### Backup ChromaDB

```bash
# Backup del directorio de persistencia
docker-compose exec backend tar -czf /tmp/chroma_backup.tar.gz /app/chroma_data

# Copiar al host
docker cp $(docker-compose ps -q backend):/tmp/chroma_backup.tar.gz ./chroma_backup.tar.gz
```

### Restaurar ChromaDB

```bash
# Restaurar desde backup
docker cp chroma_backup.tar.gz $(docker-compose ps -q backend):/tmp/
docker-compose exec backend tar -xzf /tmp/chroma_backup.tar.gz -C /
```

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend ( errores )
docker-compose logs -f --tail=100 backend | grep ERROR

# Solo API requests
docker-compose logs -f backend | grep "POST\|GET"

# Workers de Celery
docker-compose logs -f worker
```

### Ver métricas de recursos

```bash
# Uso de CPU y memoria
docker stats

# Uso de disco
docker system df

# Redes
docker network ls
```

### Logs estructurados (JSON)

El backend produce logs en formato JSON para análisis:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "service": "api",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "endpoint": "/api/v1/chat/query",
  "method": "POST",
  "status_code": 200,
  "latency_ms": 250,
  "tokens_used": 1500
}
```

---

## 🔒 Seguridad

### Checklist de Producción

- [ ] `SECRET_KEY` cambiar a valor aleatorio de 64+ caracteres
- [ ] `DEBUG=false` en producción
- [ ] `ENVIRONMENT=production`
- [ ] HTTPS habilitado (Railway/Vercel lo hacen automáticamente)
- [ ] `OPENAI_API_KEY` solo en variables de entorno, nunca en código
- [ ] Rate limiting configurado
- [ ] CORS configurado con dominios específicos
- [ ] Backup automático configurado
- [ ] Logs sin información sensible (passwords, tokens)

### Rate Limiting

El backend incluye rate limiting por defecto:

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `/api/v1/auth/*` | 10 req | 1 minuto |
| `/api/v1/chat/*` | 60 req | 1 minuto |
| `/api/v1/documents/*` | 20 req | 1 minuto |
| Otros | 100 req | 1 minuto |

### Headers de Seguridad

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=31536000`

---

## 🔍 Solución de Problemas Avanzados

### El servicio no responde

```bash
# 1. Ver estado de todos los servicios
docker-compose ps

# 2. Ver logs del servicio problemático
docker-compose logs backend

# 3. Reiniciar el servicio
docker-compose restart backend

# 4. Verificar red
docker network inspect redrive-edu_default
```

### Error de conexión a base de datos

```bash
# 1. Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# 2. Conectar manualmente
docker-compose exec postgres psql -U postgres -d redrive_edu

# 3. Verificar credenciales en .env
# DATABASE_URL debe ser correcto

# 4. Reiniciar el servicio
docker-compose restart backend
```

### ChromaDB no responde

```bash
# 1. Verificar que ChromaDB está corriendo
docker-compose ps chroma

# 2. Ver logs
docker-compose logs chroma

# 3. Reiniciar
docker-compose restart chroma

# 4. Si hay problemas de permisos
docker-compose exec backend chmod -R 755 /app/chroma_data
```

### Problemas de memoria (OOM)

```bash
# Ver uso de memoria
docker stats

# Limitar memoria de un contenedor
# En docker-compose.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G

# Limpiar recursos no utilizados
docker system prune -a
```

### Errores de migrations

```bash
# 1. Ver estado actual
docker-compose exec backend alembic current

# 2. Ver historial
docker-compose exec backend alembic history

# 3. Resetear a la última migración válida
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head

# 4. Si todo falla, hacer backup y resetear
docker-compose exec postgres pg_dump -U postgres redrive_edu > backup.sql
docker-compose exec backend alembic downgrade -1
docker-compose exec backend alembic upgrade head
```

---

## 📞 Contacto y Soporte

Para soporte técnico adicional:
- GitHub Issues: https://github.com/Oppenheimmer-droid/c3po/issues
- Documentación: https://github.com/Oppenheimmer-droid/c3po#readme

---

*Versión: 1.0.0 | Última actualización: 2025*