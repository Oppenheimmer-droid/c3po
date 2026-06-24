#!/bin/bash
# =============================================================================
# C3PO - Database Initialization Script
# =============================================================================
# Inicializa PostgreSQL y crea las tablas de la base de datos
#
# Usage: bash init-db.sh
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              C3PO - DATABASE INITIALIZATION                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar directorio
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
DATA_DIR="$HOME/c3po-data"

mkdir -p "$DATA_DIR"

# =============================================================================
# 1. Iniciar PostgreSQL
# =============================================================================
echo ""
log_info "[1/3] Iniciando PostgreSQL..."

# Inicializar directorio de datos si no existe
if [ ! -d "$HOME/../usr/var/lib/postgresql" ]; then
    log_info "Inicializando cluster de PostgreSQL..."
    pg_ctl -D "$HOME/../usr/var/lib/postgresql" initdb -o "-A trust" 2>/dev/null || {
        mkdir -p "$HOME/../usr/var/lib/postgresql"
        pg_ctl -D "$HOME/../usr/var/lib/postgresql" initdb -o "-A trust"
    }
fi

# Verificar si ya está corriendo
if ! pg_isready > /dev/null 2>&1; then
    log_info "Iniciando servicio PostgreSQL..."
    nohup pg_ctl -D "$HOME/../usr/var/lib/postgresql" -l "$DATA_DIR/postgres.log" start > /dev/null 2>&1 &
    sleep 3
fi

# Verificar estado
if pg_isready > /dev/null 2>&1; then
    log_success "PostgreSQL corriendo"
else
    log_error "No se pudo iniciar PostgreSQL"
    exit 1
fi

# =============================================================================
# 2. Crear base de datos y usuario
# =============================================================================
echo ""
log_info "[2/3] Configurando base de datos..."

DB_NAME="c3po"
DB_USER="postgres"
DB_PASS="postgres"

# Crear base de datos si no existe
if ! psql -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    log_info "Creando base de datos '$DB_NAME'..."
    createdb -U "$DB_USER" "$DB_NAME" 2>/dev/null || {
        psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
    }
    log_success "Base de datos '$DB_NAME' creada"
else
    log_info "Base de datos '$DB_NAME' ya existe"
fi

# =============================================================================
# 3. Inicializar tablas
# =============================================================================
echo ""
log_info "[3/3] Inicializando tablas..."

cd "$BACKEND_DIR"

# Configurar Python
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
export DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
export DATABASE_URL_SYNC="postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/c3po
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/c3po

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
GROQ_API_KEY=your_groq_api_key_here
GROQ_MOCK=false

# Security
SECRET_KEY=c3po-dev-secret-key-for-local-development-only-32chars

# Environment
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=*

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
EOF
    log_info "Creado archivo .env con configuración por defecto"
    log_warning "Recuerda configurar tu GROQ_API_KEY!"
fi

# Verificar si existe el script de inicialización
if [ -f "init_db.py" ]; then
    log_info "Ejecutando init_db.py..."
    python init_db.py
elif [ -f "app/models/__init__.py" ]; then
    log_info "Ejecutando migración de tablas..."
    python -c "
import asyncio
import sys
sys.path.insert(0, '.')
from app.core.database import _get_engine
from app.models import Base

async def init():
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Tablas creadas exitosamente!')
    await engine.dispose()

asyncio.run(init())
"
else
    log_warning "No se encontró script de inicialización"
fi

cd - > /dev/null

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      INICIALIZACIÓN COMPLETA                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "Base de datos lista!"
echo ""
echo "📋 Próximo paso: bash start.sh"
echo ""
