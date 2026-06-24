#!/bin/bash
# =============================================================================
# C3PO - Termux Setup Script
# =============================================================================
# Este script configura C3PO en Termux (Android)
#
# Usage: bash setup.sh
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones de logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              C3PO - TERMUX SETUP SCRIPT                            ║"
echo "║              Version 2.1.0                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar directorio del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"

# =============================================================================
# 1. Actualizar paquetes
# =============================================================================
echo ""
log_info "[1/6] Actualizando paquetes..."
pkg update -y && pkg upgrade -y
log_success "Paquetes actualizados"

# =============================================================================
# 2. Instalar paquetes base
# =============================================================================
echo ""
log_info "[2/6] Instalando paquetes base..."
BASE_PACKAGES="git curl wget nano unzip python python-pip nodejs npm"
DATABASE_PACKAGES="postgresql redis"

for pkg in $BASE_PACKAGES $DATABASE_PACKAGES; do
    if dpkg -l | grep -q "^ii  $pkg "; then
        echo "  - $pkg (ya instalado)"
    else
        echo "  - Instalando $pkg..."
        pkg install -y $pkg 2>/dev/null || log_warning "  $pkg no disponible o ya instalado"
    fi
done

# Asegurar que postgresql esté instalado
pkg install -y postgresql redis 2>/dev/null || true
log_success "Paquetes instalados"

# =============================================================================
# 3. Configurar Python
# =============================================================================
echo ""
log_info "[3/6] Configurando Python..."
pip install --upgrade pip setuptools wheel --break-system-packages 2>/dev/null || \
    pip install --upgrade pip setuptools wheel 2>/dev/null || true
log_success "Python configurado"

# =============================================================================
# 4. Clonar/Actualizar proyecto
# =============================================================================
echo ""
log_info "[4/6] Preparando proyecto..."

# Crear directorio de trabajo
mkdir -p ~/c3po-termux

# Si ya existe, actualizar
if [ -d "$PROJECT_DIR/.git" ]; then
    log_info "Proyecto ya existe, actualizando..."
    cd "$PROJECT_DIR"
    git pull origin main 2>/dev/null || git pull origin deploy 2>/dev/null || true
    cd - > /dev/null
else
    log_info "Clonando proyecto..."
    cd ~
    rm -rf c3po-termux 2>/dev/null || true
    git clone https://github.com/Oppenheimmer-droid/c3po.git c3po-termux
    cd c3po-termux
    PROJECT_DIR="$HOME/c3po-termux"
    BACKEND_DIR="$PROJECT_DIR/backend"
fi

log_success "Proyecto preparado en $PROJECT_DIR"

# =============================================================================
# 5. Instalar dependencias del backend
# =============================================================================
echo ""
log_info "[5/6] Instalando Backend..."

cd "$BACKEND_DIR"

# En Termux, no usamos venv - instalamos directamente con --break-system-packages
# Esto es necesario porque Termux tiene un sistema de paquetes especial

# Actualizar pip
pip install --upgrade pip --break-system-packages 2>/dev/null || pip install --upgrade pip 2>/dev/null || true

# Instalar dependencias con --break-system-packages para Termux
if pip install -q --break-system-packages -r requirements.txt 2>/dev/null; then
    log_success "Dependencias instaladas (break-system-packages)"
elif pip install -q -r requirements.txt --user 2>/dev/null; then
    log_success "Dependencias instaladas (user mode)"
else
    log_warning "Instalando dependencias sin flags especiales..."
    pip install -q -r requirements.txt || true
fi

# Crear directorio de datos
mkdir -p ~/../usr/var/lib/postgresql
mkdir -p ~/c3po-data/uploads
mkdir -p ~/c3po-data/chroma

cd - > /dev/null
log_success "Backend instalado"

# =============================================================================
# 6. Crear scripts de conveniencia
# =============================================================================
echo ""
log_info "[6/6] Creando scripts..."

# Copiar scripts de termux
cp "$SCRIPT_DIR"/*.sh "$PROJECT_DIR/" 2>/dev/null || true

# Crear .env si no existe
if [ ! -f "$BACKEND_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$BACKEND_DIR/.env"
        log_info "Creado archivo .env desde plantilla"
        log_warning "Recuerda configurar tu GROQ_API_KEY en backend/.env"
    fi
fi

# Hacer scripts ejecutables
chmod +x "$PROJECT_DIR"/*.sh 2>/dev/null || true

log_success "Scripts creados"

# =============================================================================
# Resumen
# =============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      CONFIGURACIÓN COMPLETADA                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Proyecto: $PROJECT_DIR"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "  1. Configurar tu API Key de Groq:"
echo "     nano $BACKEND_DIR/.env"
echo "     Edita: GROQ_API_KEY=gsk_tu_key_real"
echo ""
echo "  2. Inicializar la base de datos:"
echo "     cd $PROJECT_DIR"
echo "     bash init-db.sh"
echo ""
echo "  3. Iniciar C3PO:"
echo "     bash start.sh"
echo ""
echo "  4. Abrir en navegador:"
echo "     http://localhost:3000"
echo ""
echo "  📖 Comandos disponibles:"
echo "     bash start.sh    - Iniciar todos los servicios"
echo "     bash stop.sh     - Detener todos los servicios"
echo "     bash status.sh   - Ver estado de los servicios"
echo ""
log_success "¡Setup completado!"
echo ""
