#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    C3PO - SCRIPT DE INICIO COMPLETO                    ║
# ║                    Para ejecutar después de setup.sh                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Colores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

# Detectar directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    INICIANDO C3PO                                  ║"
echo "║                    Termux Edition v2.1.0                           ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar que existe el proyecto
if [ ! -d "$SCRIPT_DIR/backend" ] || [ ! -d "$SCRIPT_DIR/frontend" ]; then
    echo -e "${RED}✗ Error: No se encontró el proyecto C3PO${NC}"
    echo "   Ejecuta primero: bash setup.sh"
    exit 1
fi

# Función para verificar si un servicio está corriendo
is_running() {
    pgrep -x "$1" > /dev/null 2>&1
}

# 1. Iniciar PostgreSQL
echo -e "${GREEN}[1/5]${NC} Verificando PostgreSQL..."
if ! is_running postgres; then
    echo "   Iniciando PostgreSQL..."
    if [ ! -d "$HOME/.termux-postgresql" ]; then
        echo "   Creando cluster de PostgreSQL..."
        initdb -D "$HOME/.termux-postgresql" > /dev/null 2>&1
    fi
    pg_ctl -D "$HOME/.termux-postgresql" start 2>/dev/null || \
    nohup pg_ctl -D "$HOME/.termux-postgresql" start > /tmp/postgres.log 2>&1 &
    sleep 3
fi
echo -e "   ${GREEN}✓${NC} PostgreSQL corriendo"

# 2. Iniciar Redis
echo -e "${GREEN}[2/5]${NC} Verificando Redis..."
if ! is_running redis-server; then
    echo "   Iniciando Redis..."
    nohup redis-server > /tmp/redis.log 2>&1 &
    sleep 1
fi
echo -e "   ${GREEN}✓${NC} Redis corriendo"

# 3. Iniciar Backend
echo -e "${GREEN}[3/5]${NC} Iniciando Backend (FastAPI)..."
cd "$SCRIPT_DIR/backend"

# Verificar que existe el venv
if [ ! -d "venv" ]; then
    echo -e "   ${RED}✗ Error: No existe el entorno virtual${NC}"
    echo "   Ejecuta primero: bash setup.sh"
    exit 1
fi

source venv/bin/activate
export PYTHONPATH="$PWD"

# Verificar si ya está corriendo
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo -e "   ${YELLOW}⚠${NC} Backend ya está corriendo, deteniendo..."
    pkill -f "uvicorn.*app.main:app" || true
    sleep 1
fi

# Iniciar backend en segundo plano
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Verificar que inició
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Backend iniciado (PID: $BACKEND_PID)"
else
    echo -e "   ${RED}✗ Error al iniciar backend${NC}"
    tail -20 /tmp/backend.log
    exit 1
fi

# 4. Iniciar Frontend
echo -e "${GREEN}[4/5]${NC} Iniciando Frontend (Next.js)..."
cd "$SCRIPT_DIR/frontend"

# Verificar si ya está corriendo
if pgrep -f "next dev" > /dev/null; then
    echo -e "   ${YELLOW}⚠${NC} Frontend ya está corriendo, deteniendo..."
    pkill -f "next dev" || true
    sleep 1
fi

# Iniciar frontend en segundo plano
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5

# Verificar que inició
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Frontend iniciado (PID: $FRONTEND_PID)"
else
    echo -e "   ${RED}✗ Error al iniciar frontend${NC}"
    tail -20 /tmp/frontend.log
    exit 1
fi

# 5. Verificar servicios
echo -e "${GREEN}[5/5]${NC} Verificando servicios..."
sleep 2

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo -e "   ${GREEN}✓${NC} Backend API: http://localhost:8000 (Saludable)"
else
    echo -e "   ${YELLOW}⚠${NC} Backend API: http://localhost:8000 (Estado: $BACKEND_STATUS)"
fi

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      ✓ C3PO INICIADO                                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}ACCESO:${NC}"
echo ""
echo -e "  🌐  Frontend:      ${CYAN}http://localhost:3000${NC}"
echo -e "  📡  Backend API:   ${CYAN}http://localhost:8000${NC}"
echo -e "  📖  API Docs:      ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BOLD}CREDENCIALES DE PRUEBA:${NC}"
echo -e "  👤  Admin:        ${CYAN}admin@imaginary.edu${NC}"
echo -e "  🔐  Contraseña:   ${CYAN}admin123${NC}"
echo ""
echo -e "${BOLD}LOGS:${NC}"
echo -e "  📄  Backend:   tail -f /tmp/backend.log"
echo -e "  📄  Frontend:  tail -f /tmp/frontend.log"
echo -e "  📄  Postgres:   cat /tmp/postgres.log"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener todos los servicios${NC}"
echo ""

# Guardar PIDs para limpieza
echo "$BACKEND_PID" > /tmp/c3po_backend.pid
echo "$FRONTEND_PID" > /tmp/c3po_frontend.pid

# Función de limpieza
cleanup() {
    echo ""
    echo -e "${CYAN}Deteniendo servicios...${NC}"
    
    echo "   Deteniendo Backend..."
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    
    echo "   Deteniendo Frontend..."
    pkill -f "next dev" 2>/dev/null || true
    
    rm -f /tmp/c3po_backend.pid /tmp/c3po_frontend.pid
    
    echo -e "${GREEN}✓ Servicios detenidos${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Mantener el script corriendo y mostrar logs cada 30 segundos
echo -e "${BOLD}Monitoreando servicios...${NC}"
while true; do
    sleep 30
    
    # Verificar si los procesos siguen corriendo
    if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${RED}⚠ Backend dejó de funcionar${NC}"
        tail -10 /tmp/backend.log
    fi
    
    if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${RED}⚠ Frontend dejó de funcionar${NC}"
        tail -10 /tmp/frontend.log
    fi
done
