#!/bin/bash
# =============================================================================
# C3PO - Script de Despliegue Completo
# =============================================================================
# Este script despliega toda la plataforma C3PO.
#
# Uso Local (Docker):
#   ./deploy.sh           - Despliegue local con Docker Compose
#   ./deploy.sh status    - Ver estado de los servicios
#   ./deploy.sh logs      - Ver logs de los servicios
#   ./deploy.sh stop      - Detener todos los servicios
#   ./deploy.sh clean     - Eliminar todos los contenedores y volúmenes
#   ./deploy.sh init-db   - Inicializar la base de datos
#
# Uso Producción (Railway + Vercel):
#   ./deploy.sh railway   - Desplegar backend a Railway
#   ./deploy.sh vercel   - Desplegar frontend a Vercel
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Función para imprimir mensajes
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# =============================================================================
# FUNCIONES LOCALES (DOCKER)
# =============================================================================

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker no está corriendo. Iniciando dockerd..."
        sudo dockerd > /tmp/docker.log 2>&1 &
        sleep 5
        if ! docker info > /dev/null 2>&1; then
            log_error "No se pudo iniciar Docker."
            exit 1
        fi
    fi
    log_success "Docker está corriendo"
}

init_database() {
    log_info "Inicializando base de datos..."
    cd "$SCRIPT_DIR/backend"
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/c3po"
    python init_db.py
    cd - > /dev/null
    log_success "Base de datos inicializada"
}

deploy_infrastructure() {
    log_info "Desplegando servicios de infraestructura..."
    cd "$SCRIPT_DIR"
    sudo docker compose up -d postgres redis chromadb
    log_success "Servicios de infraestructura desplegados"
}

deploy_api() {
    log_info "Desplegando API..."
    cd "$SCRIPT_DIR"
    
    if ! docker image inspect c3po-backend:dev > /dev/null 2>&1; then
        log_info "Compilando imagen del backend..."
        sudo docker build -f Dockerfile -t c3po-backend:dev .
    fi
    
    sudo docker rm -f c3po-api 2>/dev/null || true
    
    sudo docker run -d --name c3po-api \
        --network c3po_c3po-network \
        -p 8001:8000 \
        -e DATABASE_URL="postgresql+asyncpg://postgres:postgres@postgres:5432/c3po" \
        -e DATABASE_URL_SYNC="postgresql+psycopg2://postgres:postgres@postgres:5432/c3po" \
        -e REDIS_URL="redis://redis:6379/0" \
        -e CHROMA_HOST=chromadb \
        -e CHROMA_PORT=8000 \
        -e SECRET_KEY="${SECRET_KEY:-c3po-dev-secret-key-for-local-development-only-32chars}" \
        -e ENVIRONMENT="${ENVIRONMENT:-development}" \
        -e DEBUG="${DEBUG:-true}" \
        -e CORS_ORIGINS="*" \
        -e GROQ_MOCK="${GROQ_MOCK:-true}" \
        -e GROQ_API_KEY="${GROQ_API_KEY:-}" \
        -e PORT=8000 \
        c3po-backend:dev
    
    log_success "API desplegada en http://localhost:8001"
}

deploy_frontend_local() {
    log_info "Desplegando Frontend..."
    cd "$SCRIPT_DIR"
    
    if ! docker image inspect c3po-frontend:dev > /dev/null 2>&1; then
        log_info "Compilando imagen del frontend..."
        sudo docker build -f Dockerfile.frontend -t c3po-frontend:dev --target development .
    fi
    
    sudo docker rm -f c3po-frontend 2>/dev/null || true
    
    sudo docker run -d --name c3po-frontend \
        --network c3po_c3po-network \
        -p 3000:3000 \
        -e NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8001}" \
        -e NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL:-http://localhost:3000}" \
        -e NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-ws://localhost:8001}" \
        c3po-frontend:dev
    
    log_success "Frontend desplegado en http://localhost:3000"
}

show_status() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "                    ESTADO DEL SISTEMA                     "
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Endpoints (Local):"
    echo "  - Backend API:    http://localhost:8001"
    echo "  - Backend Docs:   http://localhost:8001/docs"
    echo "  - Frontend:       http://localhost:3000"
    echo ""
    echo "Production URLs:"
    echo "  - Railway Backend: Configurar en Railway Dashboard"
    echo "  - Vercel Frontend: Configurar en Vercel Dashboard"
    echo ""
}

# =============================================================================
# FUNCIONES PRODUCCIÓN (RAILWAY + VERCEL)
# =============================================================================

deploy_railway() {
    log_info "${CYAN}Desplegando backend a Railway...${NC}"
    echo ""
    
    if ! command -v railway &> /dev/null; then
        log_info "Instalando Railway CLI..."
        npm i -g @railway/cli
    fi
    
    cd "$SCRIPT_DIR/backend"
    
    if [ -z "$RAILWAY_TOKEN" ]; then
        log_warning "RAILWAY_TOKEN no está configurado"
        log_info "Ejecuta: railway login"
        echo ""
        echo "O configura el token en GitHub Secrets para CI/CD"
        echo "Consulta: $SCRIPT_DIR/DEPLOY_RAILWAY_VERCEL.md"
        return 1
    fi
    
    railway up --service c3po-api
    log_success "Backend desplegado a Railway"
}

deploy_vercel() {
    log_info "${CYAN}Desplegando frontend a Vercel...${NC}"
    echo ""
    
    if ! command -v vercel &> /dev/null; then
        log_info "Instalando Vercel CLI..."
        npm i -g vercel
    fi
    
    cd "$SCRIPT_DIR/frontend"
    
    if [ -z "$VERCEL_TOKEN" ]; then
        log_warning "VERCEL_TOKEN no está configurado"
        log_info "Ejecuta: vercel login"
        echo ""
        echo "O configura el token en GitHub Secrets para CI/CD"
        echo "Consulta: $SCRIPT_DIR/DEPLOY_RAILWAY_VERCEL.md"
        return 1
    fi
    
    vercel --prod --yes --token="$VERCEL_TOKEN"
    log_success "Frontend desplegado a Vercel"
}

# =============================================================================
# MAIN
# =============================================================================

show_help() {
    echo "C3PO - Script de Despliegue"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Despliegue Local (Docker):"
    echo "  (sin argumento)   Desplegar todo localmente"
    echo "  status            Ver estado de los servicios"
    echo "  logs              Ver logs de los servicios"
    echo "  stop              Detener todos los servicios"
    echo "  clean             Eliminar contenedores y volúmenes"
    echo "  init-db           Inicializar la base de datos"
    echo ""
    echo "Despliegue Producción:"
    echo "  railway           Desplegar backend a Railway"
    echo "  vercel            Desplegar frontend a Vercel"
    echo ""
    echo "Documentation:"
    echo "  DEPLOY_RAILWAY_VERCEL.md - Guía completa de producción"
    echo ""
}

local_deploy() {
    check_docker
    deploy_infrastructure
    
    log_info "Esperando a que PostgreSQL esté listo..."
    for i in {1..30}; do
        if sudo docker exec c3po-postgres pg_isready -U postgres > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    log_info "Esperando a que Redis esté listo..."
    for i in {1..15}; do
        if sudo docker exec c3po-redis redis-cli ping > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    deploy_api
    deploy_frontend_local
    
    echo ""
    log_success "═══════════════════════════════════════════════════════════"
    log_success "    DESPLIEGUE LOCAL COMPLETADO"
    log_success "═══════════════════════════════════════════════════════════"
    echo ""
    show_status
}

stop_services() {
    log_info "Deteniendo servicios..."
    cd "$SCRIPT_DIR"
    sudo docker compose down 2>/dev/null || true
    sudo docker rm -f c3po-api c3po-frontend 2>/dev/null || true
    log_success "Servicios detenidos"
}

clean_all() {
    log_warning "Eliminando todos los contenedores y volúmenes..."
    cd "$SCRIPT_DIR"
    sudo docker compose down -v 2>/dev/null || true
    sudo docker rm -f c3po-api c3po-frontend 2>/dev/null || true
    sudo docker image prune -f
    log_success "Limpieza completada"
}

case "${1:-}" in
    status)
        check_docker
        show_status
        ;;
    logs)
        cd "$SCRIPT_DIR"
        sudo docker compose logs --tail=50
        ;;
    stop)
        stop_services
        ;;
    clean)
        clean_all
        ;;
    init-db)
        check_docker
        init_database
        ;;
    railway)
        deploy_railway
        ;;
    vercel)
        deploy_vercel
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        local_deploy
        ;;
    *)
        log_error "Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
