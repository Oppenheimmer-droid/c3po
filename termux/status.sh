#!/bin/bash
# =============================================================================
# C3PO - Status Script
# =============================================================================
# Muestra el estado de todos los servicios
#
# Usage: bash status.sh
# =============================================================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    C3PO - SERVICE STATUS                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

DATA_DIR="$HOME/c3po-data"
BACKEND_DIR="$HOME/c3po-termux/backend"
FRONTEND_DIR="$HOME/c3po-termux/frontend"

# Función para verificar servicio
check_service() {
    local name=$1
    local check_cmd=$2
    
    if eval "$check_cmd" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name"
        return 1
    fi
}

# PostgreSQL
echo "📊 Bases de datos:"
if pg_isready > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} PostgreSQL (corriendo)"
    # Mostrar bases de datos
    psql -U postgres -c "SELECT datname FROM pg_database WHERE datname NOT IN ('postgres','template0','template1');" 2>/dev/null | grep -v "datname" | grep -v "^(" | grep -v "^$" | while read db; do
        echo "     └─ $db"
    done
else
    echo -e "  ${RED}✗${NC} PostgreSQL (detenido)"
fi

echo ""

# Redis
echo "📦 Cache:"
if pgrep -x redis-server > /dev/null; then
    echo -e "  ${GREEN}✓${NC} Redis (corriendo)"
else
    echo -e "  ${RED}✗${NC} Redis (detenido)"
fi

echo ""

# Backend API
echo "🔌 Backend API:"
if curl -sf "http://localhost:8000/api/v1/health" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Backend API (corriendo en puerto 8000)"
    # Intentar obtener versión o detalles
    VERSION=$(curl -s "http://localhost:8000/api/v1/health" 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "ok")
    echo "     └─ Status: $VERSION"
elif curl -sf "http://localhost:8001/api/v1/health" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Backend API (corriendo en puerto 8001)"
else
    echo -e "  ${RED}✗${NC} Backend API (detenido)"
fi

echo ""

# Frontend
echo "🌐 Frontend:"
if curl -sf "http://localhost:3000" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend Next.js (corriendo en puerto 3000)"
else
    echo -e "  ${RED}✗${NC} Frontend Next.js (detenido)"
fi

echo ""

# URLs
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 URLs de Acceso:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""

# Logs
if [ -d "$DATA_DIR" ]; then
    echo "📝 Logs Disponibles:"
    [ -f "$DATA_DIR/backend.log" ] && echo "   Backend:  $DATA_DIR/backend.log"
    [ -f "$DATA_DIR/frontend.log" ] && echo "   Frontend: $DATA_DIR/frontend.log"
    [ -f "$DATA_DIR/postgres.log" ] && echo "   PostgreSQL: $DATA_DIR/postgres.log"
fi

echo ""
