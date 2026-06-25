#!/bin/bash
# ============================================
# C3PO - Production Deploy Script
# Branch: agents
# ============================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     C3PO Production Deploy Script         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
DEPLOY_TYPE="${1:-docker}"
ENV_FILE="${2:-$PROJECT_DIR/.env.production}"

show_help() {
    echo "Usage: ./deploy.sh [docker|railway|vercel] [.env file]"
    echo ""
    echo "Options:"
    echo "  docker    Deploy using Docker Compose (default)"
    echo "  railway   Show Railway deployment instructions"
    echo "  vercel    Show Vercel deployment instructions"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh docker                      # Docker deploy"
    echo "  ./deploy.sh docker .env.production      # With custom env file"
    echo "  ./deploy.sh railway                     # Show Railway instructions"
    echo "  ./deploy.sh vercel                     # Show Vercel instructions"
}

# Docker deployment
deploy_docker() {
    echo -e "${YELLOW}Deploying with Docker Compose...${NC}"
    
    # Check .env.production exists
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}✗ $ENV_FILE not found${NC}"
        echo -e "${YELLOW}Copy .env.production.example to .env.production and fill in values${NC}"
        exit 1
    fi
    
    # Load environment variables
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    
    echo -e "${YELLOW}Building and starting containers...${NC}"
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d --build
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Docker Deploy Complete!            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}Frontend:${NC}  http://localhost:3000"
    echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
    echo ""
}

# Railway instructions
show_railway() {
    echo -e "${YELLOW}Railway Deployment Instructions${NC}"
    echo ""
    echo "1. Go to https://railway.app"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new project"
    echo "4. Set root directory: backend"
    echo "5. Railway will auto-detect Dockerfile.prod"
    echo ""
    echo "Required Environment Variables:"
    echo -e "  ${GREEN}DATABASE_URL${NC}=postgresql+asyncpg://user:pass@host:5432/db"
    echo -e "  ${GREEN}SECRET_KEY${NC}=your-strong-secret-key"
    echo -e "  ${GREEN}OPENAI_API_KEY${NC}=sk-your-openai-key"
    echo -e "  ${GREEN}ENVIRONMENT${NC}=production"
    echo -e "  ${GREEN}DEBUG${NC}=false"
    echo ""
    echo "Railway will auto-detect:"
    echo "  - Builder: Dockerfile"
    echo "  - Dockerfile: backend/Dockerfile.prod"
    echo ""
}

# Vercel instructions
show_vercel() {
    echo -e "${YELLOW}Vercel Deployment Instructions${NC}"
    echo ""
    echo "1. Go to https://vercel.com"
    echo "2. Import your GitHub repository"
    echo "3. Set root directory: frontend"
    echo "4. Vercel will auto-detect Next.js"
    echo ""
    echo "Required Environment Variables:"
    echo -e "  ${GREEN}NEXT_PUBLIC_API_URL${NC}=https://your-railway-app.up.railway.app"
    echo -e "  ${GREEN}NEXT_PUBLIC_WS_URL${NC}=wss://your-railway-app.up.railway.app"
    echo -e "  ${GREEN}NEXT_TELEMETRY_DISABLED${NC}=1"
    echo ""
    echo "After deployment:"
    echo "1. Copy Vercel frontend URL"
    echo "2. Add it to Railway's CORS_ORIGINS"
    echo ""
}

# Check service status
check_status() {
    echo -e "${YELLOW}Checking service status...${NC}"
    echo ""
    
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
    
    # PostgreSQL
    if docker exec c3po-postgres-prod pg_isready -U c3po > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
    else
        echo -e "${RED}✗ PostgreSQL is not responding${NC}"
    fi
}

# Main
case "$DEPLOY_TYPE" in
    docker)
        deploy_docker
        check_status
        ;;
    railway)
        show_railway
        ;;
    vercel)
        show_vercel
        ;;
    status)
        check_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $DEPLOY_TYPE${NC}"
        show_help
        exit 1
        ;;
esac
