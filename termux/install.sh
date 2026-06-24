#!/bin/bash
# =============================================================================
# C3PO - Quick Install Script for Termux
# =============================================================================
# Instala C3PO en Termux con un solo comando
#
# Usage:
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/Oppenheimmer-droid/c3po/main/termux/install.sh)"
#
# O:
#   curl -fsSL https://raw.githubusercontent.com/Oppenheimmer-droid/c3po/main/termux/install.sh | bash
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
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              C3PO - QUICK INSTALL FOR TERMUX                  ║"
echo "║              Version 2.1.0                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar si estamos en Termux
if [ ! -d "/data/data/com.termux" ]; then
    log_error "Este script debe ejecutarse en Termux (Android)"
    echo ""
    echo "1. Instala Termux desde F-Droid o GitHub"
    echo "2. Abre Termux"
    echo "3. Ejecuta este comando:"
    echo ""
    echo "   bash -c \"\$(curl -fsSL https://github.com/Oppenheimmer-droid/c3po/raw/main/termux/install.sh)\""
    echo ""
    exit 1
fi

# Verificar que git está disponible
if ! command -v git &> /dev/null; then
    log_info "Instalando git..."
    pkg install -y git
fi

# Verificar que curl está disponible
if ! command -v curl &> /dev/null; then
    log_info "Instalando curl..."
    pkg install -y curl
fi

# Directorios
HOME_DIR="$HOME"
PROJECT_DIR="$HOME_DIR/c3po-termux"
TERMUX_DIR="$PROJECT_DIR/termux"

# =============================================================================
# Descargar scripts
# =============================================================================
echo ""
log_info "Descargando C3PO..."

# Clonar o actualizar repositorio
if [ -d "$PROJECT_DIR/.git" ]; then
    log_info "Proyecto ya existe, actualizando..."
    cd "$PROJECT_DIR"
    git pull origin deploy 2>/dev/null || git pull origin main 2>/dev/null
    cd - > /dev/null
else
    log_info "Clonando repositorio..."
    cd "$HOME_DIR"
    rm -rf c3po-termux 2>/dev/null || true
    git clone https://github.com/Oppenheimmer-droid/c3po.git c3po-termux
    cd c3po-termux
fi

log_success "Proyecto descargado"

# =============================================================================
# Ejecutar setup
# =============================================================================
echo ""
log_info "Ejecutando setup..."

cd "$TERMUX_DIR"
bash setup.sh

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      ¡INSTALACIÓN COMPLETA!                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "  1. Configura tu API Key de Groq:"
echo "     nano ~/c3po-termux/backend/.env"
echo "     Edita: GROQ_API_KEY=tu_key_real"
echo ""
echo "  2. Inicializa la base de datos:"
echo "     cd ~/c3po-termux"
echo "     bash termux/init-db.sh"
echo ""
echo "  3. Inicia C3PO:"
echo "     bash termux/start.sh"
echo ""
echo "  4. Abre en navegador:"
echo "     http://localhost:3000"
echo ""
