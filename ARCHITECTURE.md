# C3PO Architecture - Análisis Completo

## Diagrama de Flujo I/O

```mermaid
flowchart TB
    subgraph Internet["🌐 Internet / Cliente"]
        Client[ Browser / curl / Postman]
    end

    subgraph Vercel["☁️ Vercel - Frontend"]
        FrontendNext[ Next.js 14 App]
    end

    subgraph RailwayEdge["⚡ Railway Edge Network"]
        EdgeProxy[ Railway Hikari Proxy]
    end

    subgraph RailwayBackend["🚂 Railway Container"]
        DockerContainer[🐳 Docker Container]
        Uvicorn[ Uvicorn ASGI]
        FastAPIFastAPI[ FastAPI App]
        
        subgraph FastAPIRouters[" FastAPI Routers"]
            HealthRouter[ /api/v1/health]
            AuthRouter[ /api/v1/auth]
            UsersRouter[ /api/v1/users]
            ChatRouter[ /api/v1/chat]
            DocsRouter[ /api/v1/documents]
            EvalRouter[ /api/v1/evaluations]
            AnalyticsRouter[ /api/v1/analytics]
        end
        
        subgraph ServicesLayer[" Services Layer"]
            AuthService[ AuthService]
            GroqService[ GroqService]
            DocumentService[ DocumentService]
            AnalyticsService[ AnalyticsService]
            RAGService[ RAGService]
        end
        
        subgraph DataLayer[" Data Layer"]
            SQLAlchemyAsync[ SQLAlchemy Async Engine]
            VectorStore[ ChromaDB / Dummy]
        end
    end

    subgraph ExternalServices[" 🔌 External Services"]
        PostgresDB[ PostgreSQL]
        RedisCache[ Redis]
        GroqAPI[ Groq API]
    end

    %% Connection flows
    Client -->|HTTPS| EdgeProxy
    EdgeProxy -->|TCP :8080| DockerContainer
    DockerContainer --> Uvicorn
    Uvicorn --> FastAPIFastAPI
    FastAPIFastAPI --> FastAPIRouters
    FastAPIRouters --> ServicesLayer
    ServicesLayer --> DataLayer
    
    DataLayer -->|psycopg2/asyncpg| PostgresDB
    ServicesLayer -->|groq SDK| GroqAPI

    FrontendNext -->|fetch /api| EdgeProxy
```

## Flujo de Request/Response

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Railway Proxy
    participant D as Docker Container
    participant U as Uvicorn
    participant F as FastAPI
    participant DB as PostgreSQL

    Note over C,F: Success Path
    
    C->>R: GET /api/v1/health
    R->>D: TCP :8080
    D->>U: HTTP Request
    U->>F: ASGI Call
    F->>F: Route Match /health
    F-->>U: JSON {"status":"ok"}
    U-->>R: HTTP 200
    R-->>C: HTTP 200

    Note over C,R: Error Path - 502
    
    C->>R: GET /
    R-xD: Connection refused
    R-->>C: 502 Bad Gateway
```

## Endpoints del API

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/` | Root | No |
| GET | `/api/v1/health` | Health check | No |
| POST | `/api/v1/auth/register` | Registrar tenant | No |
| POST | `/api/v1/auth/login` | Login | No |
| GET | `/api/v1/users/me` | Usuario actual | JWT |
| POST | `/api/v1/chat` | Nuevo chat | JWT |
| GET | `/api/v1/documents` | Listar docs | JWT |
| POST | `/api/v1/evaluations/{id}/submit` | Submit eval | JWT |
| GET | `/api/v1/analytics/overview` | Analytics | JWT |

## Diagnóstico de Errores

| Código | Significado | Causa | Solución |
|--------|-------------|-------|----------|
| 502 | Bad Gateway | Container no responde | Ver logs, rebuild |
| 503 | Service Unavailable | RuntimeError startup | Configurar env vars |
| 500 | Internal Error | Exception en código | Revisar logs |

## Estado Actual

```
URL: https://c3po-production-0c24.up.railway.app
Status: 502 Bad Gateway
Error: "Application failed to respond"
Logs: Ver Console en Railway Dashboard
```

### Posibles Causas del 502

1. **Build fallando** - Dependencies no instaladas
2. **Container crash** - Exception al iniciar
3. **Wrong port** - App escuchando en puerto incorrecto
4. **Health check fail** - Railway mata el contenedor

### Solución Recomendada

1. Railway Dashboard → Deployments
2. Redeploy con "Clear Build Cache"
3. Ver logs del Console durante build
