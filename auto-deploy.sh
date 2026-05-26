#!/bin/bash

# 🚀 Script Automatizado: Preparar y hacer Push para Deployment
# Este script prepara el código y hace push a main
# Los deploys se ejecutarán automáticamente en Railway y Vercel

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🚀 AUTOMATED DEPLOYMENT PUSH SCRIPT                    ║"
echo "║        Railway + Vercel Auto-Deploy en main                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Verify everything is ready
echo "📋 Paso 1: Verificar que todo esté listo..."
echo ""

if [ ! -f "QUICK_DEPLOY.md" ]; then
    echo -e "${RED}❌ Error: QUICK_DEPLOY.md no encontrado${NC}"
    exit 1
fi

if [ ! -f "railway.json" ]; then
    echo -e "${RED}❌ Error: railway.json no encontrado${NC}"
    exit 1
fi

if [ ! -f "vercel.json" ]; then
    echo -e "${RED}❌ Error: vercel.json no encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Todos los archivos presentes${NC}"
echo ""

# Step 2: Git status
echo "📝 Paso 2: Estado de Git..."
echo ""

if [ -z "$(git status --porcelain)" ]; then
    echo "⚠️  No hay cambios que hacer commit"
    echo ""
    read -p "¿Deseas continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Abortado."
        exit 1
    fi
else
    echo "📌 Cambios detectados:"
    git status --short
    echo ""
fi

# Step 3: Show pending commits
echo "🔍 Paso 3: Verificar rama actual..."
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Rama actual: $current_branch"
echo ""

if [ "$current_branch" != "main" ]; then
    echo -e "${YELLOW}⚠️  Advertencia: No estás en la rama 'main'${NC}"
    echo "Rama actual: $current_branch"
    echo ""
    read -p "¿Deseas hacer push a $current_branch de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Abortado."
        exit 1
    fi
fi

# Step 4: Commit changes
echo "💾 Paso 4: Preparar commits..."
echo ""

if [ -n "$(git status --porcelain)" ]; then
    echo "Staging todos los cambios..."
    git add .
    
    echo ""
    echo "📝 Escribiendo mensaje de commit..."
    read -p "Mensaje de commit (por defecto: 'Deploy: Railway + Vercel'): " commit_msg
    commit_msg=${commit_msg:-"Deploy: Railway + Vercel"}
    
    git commit -m "$commit_msg"
    echo -e "${GREEN}✅ Commit creado${NC}"
else
    echo "ℹ️  No hay cambios para commit"
fi

echo ""

# Step 5: Push to remote
echo "🚀 Paso 5: Push a GitHub..."
echo ""

echo "Haciendo push a origin/$current_branch..."
git push origin $current_branch

echo -e "${GREEN}✅ Push completado${NC}"
echo ""

# Step 6: Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT INICIADO                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Los deploys se ejecutarán automáticamente:"
echo ""
echo "📦 BACKEND (Railway):"
echo "   → El Dockerfile será detectado automáticamente"
echo "   → Se ejecutará: alembic upgrade head"
echo "   → Se iniciará: uvicorn app.main:app"
echo "   → Monitorea en: https://railway.app"
echo ""
echo "🎨 FRONTEND (Vercel):"
echo "   → Se ejecutará: npm run build"
echo "   → Se deployará automáticamente"
echo "   → Monitorea en: https://vercel.com"
echo ""
echo "⏱️  Tiempo estimado de deploy: 5-15 minutos"
echo ""
echo "📊 Próximos pasos:"
echo "   1. Ve a Railway Dashboard y verifica el status del backend"
echo "   2. Ve a Vercel Dashboard y verifica el status del frontend"
echo "   3. Una vez deployed, actualiza CORS_ORIGINS en Railway"
echo "   4. Prueba la conexión entre frontend y backend"
echo ""
echo -e "${GREEN}¡Deployment en progreso! 🚀${NC}"
echo ""
