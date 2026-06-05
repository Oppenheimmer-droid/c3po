# ============================================
# RAILWAY BACKEND ENVIRONMENT VARIABLES
# ============================================
# Copy these to Railway Dashboard → Variables

# Database - Use asyncpg for async operations
DATABASE_URL="postgresql+asyncpg://postgres:HrojhTICOBDuRitjPUQkQfNPtAJjjnqz@zephyr.proxy.rlwy.net:36183/railway"
DATABASE_URL_SYNC="postgresql+psycopg2://postgres:HrojhTICOBDuRitjPUQkQfNPtAJjjnqz@zephyr.proxy.rlwy.net:36183/railway"

# Redis - Remove if not configured, or set actual values
# REDIS_URL="redis://default:YOUR_REDIS_PASSWORD@YOUR_REDIS_HOST:YOUR_REDIS_PORT"

# Python Path
PYTHONPATH="/app"

# Server
ENVIRONMENT="production"
DEBUG="false"
API_HOST="0.0.0.0"
PORT="8000"

# Security
SECRET_KEY="supersecret-change-in-production-min-32-chars"

# CORS - Comma-separated list, NOT JSON
CORS_ORIGINS="https://*.vercel.app,https://c3po-production-0c24.up.railway.app,http://localhost:3000,http://localhost:3001"
ALLOW_CREDENTIALS="true"

# OpenAI
OPENAI_API_KEY="sk-proj-YOUR_OPENAI_KEY_HERE"
OPENAI_MODEL="gpt-4o-mini"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
OPENAI_EMBEDDING_DIM="1536"

# ChromaDB - Local mode (not cloud)
CHROMA_USE_CLOUD="false"
CHROMA_HOST="chroma"
CHROMA_PORT="8000"
CHROMA_PERSIST_DIR="./chroma_data"

# ChromaDB Cloud - Disabled (only if using cloud)
# CHROMA_CLOUD_API_KEY="your_chroma_cloud_api_key_here"
# CHROMA_CLOUD_HOST="api.trychroma.com"
# CHROMA_CLOUD_PORT="443"
# CHROMA_CLOUD_ENABLE_SSL="true"
# CHROMA_CLOUD_TENANT="default_tenant"
# CHROMA_CLOUD_DATABASE="default_database"

# Frontend URL for redirects
NEXT_PUBLIC_API_URL="https://c3po-production-0c24.up.railway.app"