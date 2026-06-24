#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║               C3PO - INICIAR SOLO FRONTEND                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                 INICIANDO FRONTEND (NEXT.JS)                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar node_modules
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${RED}✗ Error: Dependencias no instaladas${NC}"
    echo "   Ejecuta primero: bash install-frontend.sh"
    exit 1
fi

cd "$FRONTEND_DIR"

echo -e "${GREEN}[1/1]${NC} Iniciando Next.js..."
echo ""

# Verificar si ya está corriendo
if pgrep -f "next dev" > /dev/null; then
    echo -e "${YELLOW}⚠${NC} Frontend ya está corriendo"
    echo "   Deteniendo proceso anterior..."
    pkill -f "next dev" || true
    sleep 1
fi

echo -e "${GREEN}✓ Frontend iniciado${NC}"
echo ""
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔄 Recargado automático activado"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener${NC}"
echo ""

# Iniciar con hot-reload
npm run dev
