# C3PO Backend Development Skill

## Purpose
Guide backend development and debugging for the C3PO FastAPI application.

## Triggers
Use this skill when the user mentions:
- "backend development"
- "add api endpoint"
- "fix backend bug"
- "run migrations"
- "add model"
- "test api"

## Project Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── api.py          # Main API router
│   │   └── v1/             # API v1 routes
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database connection
│   │   ├── security.py    # Auth & security
│   │   └── settings.py    # Settings
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py            # FastAPI app entry
├── requirements.txt
└── Dockerfile
```

## Common Tasks

### Run Backend Locally
```bash
cd /workspace/project/c3po/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Migrations
```bash
cd /workspace/project/c3po/backend
alembic upgrade head
```

### Create Migration
```bash
cd /workspace/project/c3po/backend
alembic revision --autogenerate -m "migration message"
```

### Access Database Shell
```bash
docker exec -it c3po-postgres psql -U c3po -d c3po_db
```

### Test API Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/health
```

### Check API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Adding New Endpoints

1. Create schema in `app/schemas/schemas.py`
2. Add route in `app/api/v1/` or create new file
3. Register router in `app/api/api.py`
4. Add service logic in `app/services/`

## Environment Variables
```
DATABASE_URL=postgresql://c3po:c3po_secret@localhost:5432/c3po_db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
```

## Common Issues

### Database Connection Error
- Check if PostgreSQL container is running: `docker-compose ps`
- Verify DATABASE_URL in .env
- Check logs: `docker-compose logs postgres`

### Import Errors
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python path: `echo $PYTHONPATH`

### CORS Errors
- Verify CORS_ORIGINS in .env includes frontend URL
- Check frontend API URL configuration
