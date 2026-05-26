#!/bin/bash

# 📋 Checklist de Deployment Railway + Vercel
# Ejecuta este script para verificar que todo esté listo

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🚀 DEPLOYMENT CHECKLIST: Railway + Vercel             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_mark="✅"
x_mark="❌"
warning_mark="⚠️"

# Counters
total_checks=0
passed_checks=0
warning_checks=0

# Function to check requirement
check() {
    local description=$1
    local command=$2
    
    ((total_checks++))
    echo -n "🔍 $description ... "
    
    if eval "$command" 2>/dev/null; then
        echo -e "${GREEN}${check_mark}${NC}"
        ((passed_checks++))
    else
        echo -e "${RED}${x_mark}${NC}"
    fi
}

# Function to warn
warn() {
    local description=$1
    local command=$2
    
    ((total_checks++))
    echo -n "⚠️  $description ... "
    
    if eval "$command" 2>/dev/null; then
        echo -e "${YELLOW}${warning_mark}${NC}"
        ((warning_checks++))
    else
        echo "ℹ️  (ignorable)"
    fi
}

echo ""
echo "📦 BACKEND REQUIREMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "backend/Dockerfile existe" "[ -f backend/Dockerfile ]"
check "backend/requirements.txt existe" "[ -f backend/requirements.txt ]"
check "backend/.env.railway existe" "[ -f backend/.env.railway ]"
check "railway.json existe" "[ -f railway.json ]"
check "backend/pyproject.toml existe" "[ -f backend/pyproject.toml ]"
check "backend/app/main.py existe" "[ -f backend/app/main.py ]"

echo ""
echo "🎨 FRONTEND REQUIREMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "frontend/package.json existe" "[ -f frontend/package.json ]"
check "frontend/next.config.js existe" "[ -f frontend/next.config.js ]"
check "frontend/.env.vercel existe" "[ -f frontend/.env.vercel ]"
check "vercel.json existe" "[ -f vercel.json ]"
check "frontend/src/app/page.tsx existe" "[ -f frontend/src/app/page.tsx ]"

echo ""
echo "📚 DOCUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "DEPLOY_STEPS.md existe" "[ -f DEPLOY_STEPS.md ]"
check "DEPLOYMENT_GUIDE.md existe" "[ -f DEPLOYMENT_GUIDE.md ]"
check "README.md existe" "[ -f README.md ]"

echo ""
echo "🔐 GIT & ENVIRONMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check ".gitignore existe" "[ -f .gitignore ]"
check ".git/config existe" "[ -f .git/config ]"
check ".env.example existe" "[ -f .env.example ]"

echo ""
echo "🔧 SYSTEM TOOLS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

warn "Docker instalado" "command -v docker >/dev/null 2>&1"
warn "Git instalado" "command -v git >/dev/null 2>&1"
warn "Node.js 18+ instalado" "node --version 2>/dev/null | grep -qE 'v(18|19|20)'"
warn "Python 3.11+ instalado" "python3 --version 2>/dev/null | grep -qE '3.1[1-9]'"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    📊 RESULTS SUMMARY                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "Total checks: $total_checks"
echo -e "Passed: ${GREEN}$passed_checks${NC}"
if [ $warning_checks -gt 0 ]; then
    echo -e "Warnings: ${YELLOW}$warning_checks${NC}"
fi
echo ""

# Final result
if [ $passed_checks -eq $total_checks ]; then
    echo -e "${GREEN}✅ ¡TODOS LOS CHECKS PASARON!${NC}"
    echo ""
    echo "📝 Próximos pasos:"
    echo "  1. Asegúrate de haber generado SECRET_KEY"
    echo "  2. Configura tu API key de OpenAI"
    echo "  3. Crea cuentas en Railway y Vercel"
    echo "  4. Sigue el DEPLOY_STEPS.md para el deployment"
    echo ""
    exit 0
else
    echo -e "${RED}❌ ALGUNOS CHECKS FALLARON${NC}"
    echo ""
    echo "⚠️  Por favor, revisa los errores arriba e intenta nuevamente"
    echo ""
    exit 1
fi
