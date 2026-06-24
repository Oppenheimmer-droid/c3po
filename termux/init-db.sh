#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    C3PO - INICIALIZAR BASE DE DATOS                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Colores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                INICIALIZANDO BASE DE DATOS                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar PostgreSQL
echo -e "${GREEN}[1/4]${NC} Verificando PostgreSQL..."

if ! pgrep -x "postgres" > /dev/null; then
    echo "   Iniciando PostgreSQL..."
    if [ ! -d "$HOME/.termux-postgresql" ]; then
        initdb -D "$HOME/.termux-postgresql" > /dev/null 2>&1
    fi
    pg_ctl -D "$HOME/.termux-postgresql" start 2>/dev/null || \
    nohup pg_ctl -D "$HOME/.termux-postgresql" start > /tmp/postgres.log 2>&1 &
    sleep 3
fi
echo -e "   ${GREEN}✓${NC} PostgreSQL corriendo"

# Crear base de datos
echo -e "${GREEN}[2/4]${NC} Configurando base de datos..."
dropdb c3po 2>/dev/null || true
createdb c3po 2>/dev/null || true
psql -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || true
echo -e "   ${GREEN}✓${NC} Base de datos 'c3po' lista"

# Ir al backend
cd "$SCRIPT_DIR/backend"

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Error: No existe el entorno virtual${NC}"
    echo "   Ejecuta primero: bash setup.sh"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate
export PYTHONPATH="$PWD"

# Ejecutar inicialización
echo -e "${GREEN}[3/4]${NC} Ejecutando init_db.py..."
python init_db.py

# Ejecutar seed data
echo -e "${GREEN}[4/4]${NC} Ejecutando seed_data.py (datos de prueba)..."
python seed_data.py

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗"
echo "║                ✓ BASE DE DATOS INICIALIZADA                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}CREDENCIALES DE PRUEBA:${NC}"
echo ""
echo -e "  👤  Admin:         ${CYAN}admin@imaginary.edu${NC}"
echo -e "  🔐  Contraseña:    ${CYAN}admin123${NC}"
echo ""
echo -e "  👤  Profesor:      ${CYAN}prof.martinez@imaginary.edu${NC}"
echo -e "  🔐  Contraseña:    ${CYAN}teacher123${NC}"
echo ""
echo -e "  👤  Estudiante:    ${CYAN}sofia.perez@imaginary.edu${NC}"
echo -e "  🔐  Contraseña:    ${CYAN}student123${NC}"
echo ""
