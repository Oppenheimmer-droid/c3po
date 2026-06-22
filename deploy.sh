#!/bin/bash
# =============================================================================
# C3PO - Script de Despliegue Completo
# =============================================================================
# Este script despliega toda la plataforma C3PO usando Docker Compose.
#
# Uso:
#   ./deploy.sh           - Despliegue completo
#   ./deploy.sh status     - Ver estado de los servicios
#   ./deploy.sh logs       - Ver logs de todos los servicios
#   ./deploy.sh stop       - Detener todos los servicios
#   ./deploy.sh restart    - Reiniciar todos los servicios
#   ./deploy.sh clean      - Eliminar todos los contenedores y volúmenes
#   ./deploy.sh init-db    - Inicializar la base de datos
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker no está corriendo. Iniciando dockerd..."
        sudo dockerd > /tmp/docker.log 2>&1 &
        sleep 5
        if ! docker info > /dev/null 2>&1; then
            log_error "No se pudo iniciar Docker. Verifica los permisos."
            exit 1
        fi
    fi
    log_success "Docker está corriendo"
}

# Inicializar base de datos
init_database() {
    log_info "Inicializando base de datos..."
    cd "$(dirname "$0")/backend"
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/c3po"
    python init_db.py
    cd - > /dev/null
    log_success "Base de datos inicializada"
}

# Desplegar servicios de infraestructura
deploy_infrastructure() {
    log_info "Desplegando servicios de infraestructura..."
    cd "$(dirname "$0")"
    sudo docker compose up -d postgres redis chromadb
    log_success "Servicios de infraestructura desplegados"
}

# Desplegar API
deploy_api() {
    log_info "Desplegando API..."
    
    # Compilar imagen si no existe
    if ! docker image inspect c3po-backend:dev > /dev/null 2>&1; then
        log_info "Compilando imagen del backend..."
        sudo docker build -f Dockerfile -t c3po-backend:dev .
    fi
    
    # Detener contenedor anterior si existe
    sudo docker rm -f c3po-api 2>/dev/null || true
    
    # Iniciar nuevo contenedor
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

# Desplegar Frontend
deploy_frontend() {
    log_info "Desplegando Frontend..."
    
    # Compilar imagen si no existe
    if ! docker image inspect c3po-frontend:dev > /dev/null 2>&1; then
        log_info "Compilando imagen del frontend..."
        sudo docker build -f Dockerfile.frontend -t c3po-frontend:dev --target development .
    fi
    
    # Detener contenedor anterior si existe
    sudo docker rm -f c3po-frontend 2>/dev/null || true
    
    # Iniciar nuevo contenedor
    sudo docker run -d --name c3po-frontend \
        --network c3po_c3po-network \
        -p 3000:3000 \
        -e NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8001}" \
        -e NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL:-http://localhost:3000}" \
        -e NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-ws://localhost:8001}" \
        c3po-frontend:dev
    
    log_success "Frontend desplegado en http://localhost:3000"
}

# Ver estado
show_status() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "                    ESTADO DEL SISTEMA                     "
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Endpoints:"
    echo "  - Backend API:    http://localhost:8001"
    echo "  - Backend Docs:   http://localhost:8001/docs"
    echo "  - Frontend:       http://localhost:3000"
    echo "  - PostgreSQL:     localhost:5432"
    echo "  - Redis:          localhost:6379"
    echo "  - ChromaDB:       localhost:8000"
    echo ""
    
    # Verificar salud de servicios
    echo "Verificación de salud:"
    if curl -sf http://localhost:8001/api/v1/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Backend API"
    else
        echo -e "  ${RED}✗${NC} Backend API"
    fi
    
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Frontend"
    else
        echo -e "  ${RED}✗${NC} Frontend"
    fi
    
    if sudo docker exec c3po-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} PostgreSQL"
    else
        echo -e "  ${RED}✗${NC} PostgreSQL"
    fi
    
    if sudo docker exec c3po-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Redis"
    else
        echo -e "  ${RED}✗${NC} Redis"
    fi
    
    echo ""
}

# Mostrar logs
show_logs() {
    echo "═══════════════════════════════════════════════════════════"
    echo "                        LOGS                               "
    echo "═══════════════════════════════════════════════════════════"
    sudo docker compose logs --tail=50
}

# Detener servicios
stop_services() {
    log_info "Deteniendo servicios..."
    sudo docker compose down 2>/dev/null || true
    sudo docker rm -f c3po-api c3po-frontend 2>/dev/null || true
    log_success "Servicios detenidos"
}

# Reiniciar servicios
restart_services() {
    stop_services
    deploy
}

# Limpiar todo
clean_all() {
    log_warning "Eliminando todos los contenedores y volúmenes..."
    sudo docker compose down -v 2>/dev/null || true
    sudo docker rm -f c3po-api c3po-frontend 2>/dev/null || true
    sudo docker image prune -f
    log_success "Limpieza completada"
}

# Despliegue completo
deploy() {
    log_info "Iniciando despliegue completo de C3PO..."
    echo ""
    
    check_docker
    deploy_infrastructure
    
    # Esperar a que servicios estén healthy
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
    deploy_frontend
    
    echo ""
    log_success "═══════════════════════════════════════════════════════════"
    log_success "         DESPLIEGUE COMPLETADO EXITOSAMENTE"
    log_success "═══════════════════════════════════════════════════════════"
    echo ""
    show_status
}

# Mostrar ayuda
show_help() {
    echo "C3PO - Script de Despliegue Completo"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  (sin argumento)  Desplegar todo el sistema"
    echo "  status           Ver estado de los servicios"
    echo "  logs             Ver logs de los servicios"
    echo "  stop             Detener todos los servicios"
    echo "  restart          Reiniciar todos los servicios"
    echo "  clean            Eliminar contenedores y volúmenes"
    echo "  init-db          Inicializar la base de datos"
    echo "  help             Mostrar esta ayuda"
    echo ""
}

# Main
case "${1:-}" in
    status)
        check_docker
        show_status
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    clean)
        clean_all
        ;;
    init-db)
        check_docker
        init_database
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        deploy
        ;;
    *)
        log_error "Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
