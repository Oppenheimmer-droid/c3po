#!/bin/bash
# ============================================
# C3PO - Quick Start Script
# Auto-executable for local development
# ============================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Config
PROJECT_NAME="C3PO"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ${PROJECT_NAME} - Quick Start Script      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed${NC}"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
    
    # Check .env file
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${YELLOW}⚠ Please edit .env and add your API keys!${NC}"
    else
        echo -e "${GREEN}✓ .env file found${NC}"
    fi
}

# Start services
start_services() {
    echo ""
    echo -e "${YELLOW}Starting services...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Pull latest images
    echo -e "${BLUE}Pulling latest Docker images...${NC}"
    docker-compose pull || true
    
    # Build and start containers
    echo -e "${BLUE}Building and starting containers...${NC}"
    docker-compose up -d --build
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Services Started! 🚀               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}Frontend:${NC}  http://localhost:3000"
    echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
    echo -e "  ${BLUE}ChromaDB:${NC}  http://localhost:8001"
    echo ""
}

# Show logs
show_logs() {
    echo ""
    echo -e "${YELLOW}Showing logs (Ctrl+C to exit)...${NC}"
    echo ""
    cd "$PROJECT_DIR"
    docker-compose logs -f
}

# Stop services
stop_services() {
    echo ""
    echo -e "${YELLOW}Stopping services...${NC}"
    cd "$PROJECT_DIR"
    docker-compose down
    echo -e "${GREEN}✓ Services stopped${NC}"
}

# Reset everything
reset_all() {
    echo -e "${RED}⚠ This will delete ALL data (database, vectors, etc.)!${NC}"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Resetting everything...${NC}"
        cd "$PROJECT_DIR"
        docker-compose down -v --rmi local
        rm -rf postgres_data redis_data chroma_data 2>/dev/null || true
        echo -e "${GREEN}✓ Everything reset${NC}"
    else
        echo -e "${BLUE}Cancelled${NC}"
    fi
}

# Health check
health_check() {
    echo ""
    echo -e "${YELLOW}Running health checks...${NC}"
    
    # Backend
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
    else
        echo -e "${RED}✗ Backend is not responding${NC}"
    fi
    
    # Frontend
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is healthy${NC}"
    else
        echo -e "${RED}✗ Frontend is not responding${NC}"
    fi
    
    # ChromaDB
    if curl -sf http://localhost:8001/api/v1/collections > /dev/null 2>&1; then
        echo -e "${GREEN}✓ ChromaDB is healthy${NC}"
    else
        echo -e "${RED}✗ ChromaDB is not responding${NC}"
    fi
}

# Show help
show_help() {
    echo "Usage: ./start.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services (default)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        Show logs"
    echo "  reset       Reset all data and containers"
    echo "  health      Run health checks"
    echo "  help        Show this help"
    echo ""
}

# Main
case "${1:-start}" in
    start)
        check_prerequisites
        start_services
        health_check
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        health_check
        ;;
    logs)
        show_logs
        ;;
    reset)
        reset_all
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
