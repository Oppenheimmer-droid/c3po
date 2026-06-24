#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║               C3PO - DETENER TODOS LOS SERVICIOS                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                DETENIENDO SERVICIOS C3PO                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detener Backend
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo -e "${YELLOW}Deteniendo Backend...${NC}"
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    echo -e "${GREEN}✓ Backend detenido${NC}"
else
    echo -e "${CYAN}Backend no estaba corriendo${NC}"
fi

# Detener Frontend
if pgrep -f "next dev" > /dev/null; then
    echo -e "${YELLOW}Deteniendo Frontend...${NC}"
    pkill -f "next dev" 2>/dev/null || true
    echo -e "${GREEN}✓ Frontend detenido${NC}"
else
    echo -e "${CYAN}Frontend no estaba corriendo${NC}"
fi

# Detener Redis
if pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}Deteniendo Redis...${NC}"
    redis-cli shutdown 2>/dev/null || pkill -x redis-server 2>/dev/null || true
    echo -e "${GREEN}✓ Redis detenido${NC}"
else
    echo -e "${CYAN}Redis no estaba corriendo${NC}"
fi

# Limpiar PIDs
rm -f /tmp/c3po_backend.pid /tmp/c3po_frontend.pid

echo ""
echo -e "${GREEN}✓ Todos los servicios detenidos${NC}"
