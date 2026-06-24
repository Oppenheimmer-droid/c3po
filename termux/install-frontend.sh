#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║               C3PO - INSTALAR DEPENDENCIAS FRONTEND                  ║
# ║                    Versión para Termux                               ║
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
echo "║            INSTALANDO DEPENDENCIAS FRONTEND                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$FRONTEND_DIR"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Error: Node.js no está instalado${NC}"
    echo "   Ejecuta: pkg install nodejs"
    exit 1
fi

echo -e "${GREEN}[1/3]${NC} Verificando Node.js..."
node --version
npm --version

echo -e "${GREEN}[2/3]${NC} Instalando dependencias npm..."
# Ignorar engine check para Termux compatibility
npm install --ignore-engines

echo -e "${GREEN}[3/3]${NC} Verificando instalación..."
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} Dependencias instaladas correctamente"
    echo "   $(ls node_modules | wc -l) paquetes"
else
    echo -e "${RED}✗ Error: node_modules no se creó${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Frontend listo${NC}"
echo "   Ejecuta: cd $FRONTEND_DIR && npm run dev"
