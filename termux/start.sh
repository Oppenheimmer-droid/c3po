#!/bin/bash
# =============================================================================
# C3PO - Start Script
# =============================================================================
# Inicia todos los servicios de C3PO (Backend + Frontend)
#
# Usage: bash start.sh
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    C3PO - STARTING SERVICES                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar directorio
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
DATA_DIR="$HOME/c3po-data"

# =============================================================================
# Funciones de servicio
# =============================================================================

start_postgres() {
    log_info "Iniciando PostgreSQL..."
    if pg_isready > /dev/null 2>&1; then
        log_success "PostgreSQL ya está corriendo"
    else
        mkdir -p "$HOME/../usr/var/lib/postgresql"
        nohup pg_ctl -D "$HOME/../usr/var/lib/postgresql" -l "$DATA_DIR/postgres.log" start > /dev/null 2>&1 &
        sleep 3
        if pg_isready > /dev/null 2>&1; then
            log_success "PostgreSQL iniciado"
        else
            log_error "Error al iniciar PostgreSQL"
            return 1
        fi
    fi
}

start_redis() {
    log_info "Iniciando Redis..."
    if pgrep -x redis-server > /dev/null; then
        log_success "Redis ya está corriendo"
    else
        nohup redis-server --daemonize yes > /dev/null 2>&1 &
        sleep 2
        if pgrep -x redis-server > /dev/null; then
            log_success "Redis iniciado"
        else
            log_error "Error al iniciar Redis"
            return 1
        fi
    fi
}

start_backend() {
    log_info "Iniciando Backend API..."
    
    cd "$BACKEND_DIR"
    
    # Configurar variables de entorno
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:postgres@localhost:5432/c3po}"
    export DATABASE_URL_SYNC="${DATABASE_URL_SYNC:-postgresql://postgres:postgres@localhost:5432/c3po}"
    export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
    export PORT="${PORT:-8000}"
    export ENVIRONMENT="${ENVIRONMENT:-development}"
    export DEBUG="${DEBUG:-true}"
    
    # Activar venv si existe
    if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
        source "$BACKEND_DIR/venv/bin/activate"
    fi
    
    # Iniciar en background
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload > "$DATA_DIR/backend.log" 2>&1 &
    
    sleep 3
    
    # Verificar si inició
    if curl -sf "http://localhost:$PORT/api/v1/health" > /dev/null 2>&1; then
        log_success "Backend API iniciado en http://localhost:$PORT"
        log_info "Documentación API: http://localhost:$PORT/docs"
    else
        log_warning "Backend iniciando... (puede tardar unos segundos)"
    fi
    
    cd - > /dev/null
}

start_frontend() {
    log_info "Iniciando Frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Configurar API URL
    export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
    export NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL:-http://localhost:3000}"
    export NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-ws://localhost:8000}"
    
    # Iniciar en background
    nohup npm run dev > "$DATA_DIR/frontend.log" 2>&1 &
    
    sleep 5
    
    # Verificar si inició
    if curl -sf "http://localhost:3000" > /dev/null 2>&1; then
        log_success "Frontend iniciado en http://localhost:3000"
    else
        log_warning "Frontend iniciando... (puede tardar unos segundos)"
    fi
    
    cd - > /dev/null
}

show_status() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "                       SERVICE STATUS                            "
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""
    
    # PostgreSQL
    if pg_isready > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} PostgreSQL"
    else
        echo -e "  ${RED}✗${NC} PostgreSQL"
    fi
    
    # Redis
    if pgrep -x redis-server > /dev/null; then
        echo -e "  ${GREEN}✓${NC} Redis"
    else
        echo -e "  ${RED}✗${NC} Redis"
    fi
    
    # Backend
    if curl -sf "http://localhost:8000/api/v1/health" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Backend API (port 8000)"
    else
        echo -e "  ${YELLOW}○${NC} Backend API (starting...)"
    fi
    
    # Frontend
    if curl -sf "http://localhost:3000" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Frontend (port 3000)"
    else
        echo -e "  ${YELLOW}○${NC} Frontend (starting...)"
    fi
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""
    echo "🌐 Accesos:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📝 Logs:"
    echo "   Backend:  tail -f $DATA_DIR/backend.log"
    echo "   Frontend:  tail -f $DATA_DIR/frontend.log"
    echo "   PostgreSQL: tail -f $DATA_DIR/postgres.log"
    echo ""
    echo "🛑 Para detener: bash stop.sh"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

# Crear directorio de datos
mkdir -p "$DATA_DIR"

# Verificar que el proyecto existe
if [ ! -d "$BACKEND_DIR" ]; then
    log_error "Backend no encontrado en $BACKEND_DIR"
    echo "Ejecuta primero: bash setup.sh"
    exit 1
fi

# Iniciar servicios
echo ""
log_info "Iniciando servicios..."
echo ""

start_postgres
start_redis
start_backend
start_frontend

# Mostrar estado
sleep 2
show_status
