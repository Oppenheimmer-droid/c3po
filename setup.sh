#!/bin/bash
# ============================================
# C3PO - Setup Script
# First-time setup and installation
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
echo -e "${BLUE}║     C3PO - Setup Script v1.0.0             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1/5: Checking prerequisites...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required but not installed. Aborting.${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose is required but not installed. Aborting.${NC}"; exit 1; }
echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Step 2: Setup environment
echo ""
echo -e "${YELLOW}Step 2/5: Setting up environment...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠ Please edit .env and add your OPENAI_API_KEY!${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

# Step 3: Create directories
echo ""
echo -e "${YELLOW}Step 3/5: Creating directories...${NC}"
mkdir -p postgres_data redis_data chroma_data
chmod +x start.sh
echo -e "${GREEN}✓ Directories created${NC}"

# Step 4: Build Docker images
echo ""
echo -e "${YELLOW}Step 4/5: Building Docker images...${NC}"
cd "$PROJECT_DIR"
docker-compose build --no-cache
echo -e "${GREEN}✓ Docker images built${NC}"

# Step 5: Start services
echo ""
echo -e "${YELLOW}Step 5/5: Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Setup Complete! 🎉               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Edit ${YELLOW}.env${NC} and add your ${YELLOW}OPENAI_API_KEY${NC}"
echo -e "  2. Run ${YELLOW}./start.sh health${NC} to check status"
echo -e "  3. Access:"
echo -e "     - Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "     - Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "     - API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
