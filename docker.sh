#!/bin/bash
# ============================================
# C3PO Docker Management Script
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

show_help() {
    echo "C3PO Docker Management Script"
    echo ""
    echo "Usage: ./docker.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start         Start all services (development)"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  logs          Show logs from all services"
    echo "  logs-api      Show logs from API only"
    echo "  logs-frontend Show logs from frontend only"
    echo "  ps            Show running containers"
    echo "  build         Build all Docker images"
    echo "  clean         Remove all containers and volumes"
    echo "  status        Check health status of services"
    echo "  shell-api     Open shell in API container"
    echo "  help          Show this help message"
    echo ""
}

# Check if .env exists
check_env() {
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        log_info "Please edit .env and add your API keys"
    fi
}

# Start services
start_services() {
    check_env
    log_info "Starting C3PO services..."
    docker compose up -d
    log_success "Services started!"
    echo ""
    echo "Services:"
    echo "  - API:      http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Postgres: localhost:5432"
    echo "  - Redis:    localhost:6379"
    echo "  - ChromaDB: localhost:8000"
}

# Stop services
stop_services() {
    log_info "Stopping C3PO services..."
    docker compose down
    log_success "Services stopped!"
}

# Restart services
restart_services() {
    stop_services
    start_services
}

# Show logs
show_logs() {
    docker compose logs -f --tail=100
}

show_api_logs() {
    docker compose logs -f api --tail=100
}

show_frontend_logs() {
    docker compose logs -f frontend --tail=100
}

# Show running containers
show_ps() {
    docker compose ps
}

# Build images
build_images() {
    log_info "Building Docker images..."
    docker compose build --no-cache
    log_success "Images built!"
}

# Clean up
clean_up() {
    log_warning "This will remove ALL containers and volumes!"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker compose down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup complete!"
    else
        log_info "Cleanup cancelled"
    fi
}

# Check status
check_status() {
    echo ""
    echo "=== Service Status ==="
    echo ""
    
    # API Health
    if curl -sf http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "API:        ${GREEN}✓ Running${NC} - http://localhost:8000"
    else
        echo -e "API:        ${RED}✗ Not responding${NC}"
    fi
    
    # Frontend Health
    if curl -sf http://localhost:3000/ > /dev/null 2>&1; then
        echo -e "Frontend:   ${GREEN}✓ Running${NC} - http://localhost:3000"
    else
        echo -e "Frontend:   ${RED}✗ Not responding${NC}"
    fi
    
    # Postgres
    if docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "Postgres:   ${GREEN}✓ Running${NC} - localhost:5432"
    else
        echo -e "Postgres:   ${RED}✗ Not responding${NC}"
    fi
    
    # Redis
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "Redis:      ${GREEN}✓ Running${NC} - localhost:6379"
    else
        echo -e "Redis:      ${RED}✗ Not responding${NC}"
    fi
    
    # ChromaDB
    if curl -sf http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
        echo -e "ChromaDB:   ${GREEN}✓ Running${NC} - localhost:8000"
    else
        echo -e "ChromaDB:   ${RED}✗ Not responding${NC}"
    fi
    
    echo ""
}

# Shell into API container
shell_api() {
    docker compose exec api /bin/sh
}

# Main
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    logs-api)
        show_api_logs
        ;;
    logs-frontend)
        show_frontend_logs
        ;;
    ps)
        show_ps
        ;;
    build)
        build_images
        ;;
    clean)
        clean_up
        ;;
    status)
        check_status
        ;;
    shell-api)
        shell_api
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac