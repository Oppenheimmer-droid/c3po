#!/bin/bash
# =============================================================================
# C3PO - Stop Script
# =============================================================================
# Detiene todos los servicios de C3PO
#
# Usage: bash stop.sh
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    C3PO - STOPPING SERVICES                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Detener Backend
log_info "Deteniendo Backend API..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "python.*uvicorn" 2>/dev/null || true
log_success "Backend detenido"

# Detener Frontend
log_info "Deteniendo Frontend..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "node.*next" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
log_success "Frontend detenido"

# Detener Redis
log_info "Deteniendo Redis..."
pkill -x redis-server 2>/dev/null || true
log_success "Redis detenido"

# Detener PostgreSQL (opcional - recomendado mantenerlo)
# pg_ctl -D "$HOME/../usr/var/lib/postgresql" stop 2>/dev/null || true

echo ""
log_success "Todos los servicios han sido detenidos"
echo ""
echo "💡 Para iniciar nuevamente: bash start.sh"
echo ""
