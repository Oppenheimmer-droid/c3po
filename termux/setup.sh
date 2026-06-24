#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                   C3PO - TERMUX SETUP SCRIPT                          ║
# ║               Install dependencies for Android (Termux)                  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# USO: bash setup.sh
#
# Este script instala todas las dependencias necesarias para ejecutar C3PO
# en Termux (Android).
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Directorio del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              C3PO - TERMUX SETUP SCRIPT                          ║"
echo "║              Version 2.1.0                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}✗ Error: Este script debe ejecutarse en Termux${NC}"
    exit 1
fi

# Actualizar paquetes
echo -e "${GREEN}[1/5]${NC} Actualizando paquetes..."
pkg update -y && pkg upgrade -y

# Instalar paquetes base
echo -e "${GREEN}[2/5]${NC} Instalando paquetes base..."
pkg install -y git curl wget nano unzip python python-pip nodejs npm postgresql redis bash-completion

# Configurar Python
echo -e "${GREEN}[3/5]${NC} Configurando Python..."
mkdir -p ~/.config/pip
cat > ~/.config/pip/pip.conf << 'EOF'
[global]
user = true
break-system-packages = true
EOF
pip install --upgrade pip setuptools wheel

# Instalar backend
echo -e "${GREEN}[4/5]${NC} Instalando Backend..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/c3po
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=c3po
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
SECRET_KEY=change-me-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
AI_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_USE_CLOUD=false
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    echo -e "${YELLOW}⚠ Archivo .env creado. EDITALO y añade tu GROQ_API_KEY${NC}"
fi

# Instalar frontend
echo -e "${GREEN}[5/5]${NC} Instalando Frontend..."
cd "$SCRIPT_DIR/frontend"
npm install

# Volver al directorio del proyecto
cd "$SCRIPT_DIR"

# Hacer ejecutables los scripts
chmod +x *.sh 2>/dev/null || true

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗"
echo "║              ✓ INSTALACIÓN COMPLETADA                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}SIGUIENTES PASOS:${NC}"
echo ""
echo "1. ${YELLOW}Configura tu API Key de Groq:${NC}"
echo "   nano backend/.env"
echo "   → Edita: GROQ_API_KEY=gsk_tu_key_real"
echo ""
echo "2. ${YELLOW}Inicializa la base de datos:${NC}"
echo "   bash init-db.sh"
echo ""
echo "3. ${YELLOW}Inicia todos los servicios:${NC}"
echo "   bash start.sh"
echo ""
echo "4. ${YELLOW}Abre en tu navegador:${NC}"
echo "   http://localhost:3000"
echo ""
echo -e "${GREEN}¡Disfruta C3PO en tu Android! 🎓${NC}"
