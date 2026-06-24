#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                 C3PO - INICIAR SOLO BACKEND                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                 INICIANDO BACKEND (FASTAPI)                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar entorno virtual
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${RED}✗ Error: No existe el entorno virtual${NC}"
    echo "   Ejecuta primero: bash setup.sh"
    exit 1
fi

# Iniciar PostgreSQL si no está
if ! pgrep -x "postgres" > /dev/null; then
    echo -e "${GREEN}[1/3]${NC} Iniciando PostgreSQL..."
    if [ ! -d "$HOME/.termux-postgresql" ]; then
        initdb -D "$HOME/.termux-postgresql" > /dev/null 2>&1
    fi
    pg_ctl -D "$HOME/.termux-postgresql" start 2>/dev/null || \
    nohup pg_ctl -D "$HOME/.termux-postgresql" start > /tmp/postgres.log 2>&1 &
    sleep 2
fi
echo -e "${GREEN}✓${NC} PostgreSQL corriendo"

# Iniciar Redis si no está
if ! pgrep -x "redis-server" > /dev/null; then
    echo -e "${GREEN}[2/3]${NC} Iniciando Redis..."
    nohup redis-server > /tmp/redis.log 2>&1 &
    sleep 1
fi
echo -e "${GREEN}✓${NC} Redis corriendo"

# Iniciar Backend
echo -e "${GREEN}[3/3]${NC} Iniciando FastAPI..."
cd "$BACKEND_DIR"
source venv/bin/activate
export PYTHONPATH="$PWD"

# Verificar si ya está corriendo
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo -e "${YELLOW}⚠${NC} Backend ya está corriendo"
    echo "   Deteniendo proceso anterior..."
    pkill -f "uvicorn.*app.main:app" || true
    sleep 1
fi

echo ""
echo -e "${GREEN}✓ Backend iniciado${NC}"
echo ""
echo "  📡 Backend:   http://localhost:8000"
echo "  📖 API Docs:  http://localhost:8000/docs"
echo "  ❤️  Health:   http://localhost:8000/api/v1/health"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener${NC}"
echo ""

# Iniciar con hot-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
