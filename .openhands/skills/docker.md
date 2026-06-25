# C3PO Docker Skill

## Purpose
Manage Docker containers and services for the C3PO project.

## Triggers
Use this skill when the user mentions:
- "docker compose"
- "start services"
- "stop containers"
- "view logs"
- "reset docker"
- "rebuild containers"

## Commands

### Start All Services
```bash
cd /workspace/project/c3po
docker-compose up -d
```

### Stop All Services
```bash
cd /workspace/project/c3po
docker-compose down
```

### View Logs
```bash
cd /workspace/project/c3po
docker-compose logs -f [service_name]
```

### Rebuild Containers
```bash
cd /workspace/project/c3po
docker-compose up -d --build
```

### Reset Everything (DANGER)
```bash
cd /workspace/project/c3po
docker-compose down -v
rm -rf postgres_data redis_data chroma_data
```

### Health Check
```bash
curl -f http://localhost:8000/health  # Backend
curl -f http://localhost:3000  # Frontend
curl -f http://localhost:8001/api/v1/collections  # ChromaDB
```

## Service Names
- `c3po-postgres` - PostgreSQL database
- `c3po-redis` - Redis cache
- `c3po-chroma` - ChromaDB vector store
- `c3po-backend` - FastAPI backend
- `c3po-frontend` - Next.js frontend

## Notes
- Always run commands from the project root `/workspace/project/c3po`
- Use `docker-compose logs -f` without service name to see all logs
- Health checks are automatic via docker-compose healthcheck
