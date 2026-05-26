#!/bin/bash

# 🚀 Script de Pre-Deployment: Verificación de Build
# Ejecuta esto localmente ANTES de hacer push a main

set -e

echo "🔍 Verificando Backend..."

# Verificar que el Dockerfile existe
if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ Error: backend/Dockerfile no encontrado"
    exit 1
fi

# Verificar dependencias de Python
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: backend/requirements.txt no encontrado"
    exit 1
fi

# Verificar configuración de Railway
if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json no encontrado"
    exit 1
fi

echo "✅ Backend verificado"

echo ""
echo "🔍 Verificando Frontend..."

# Verificar que package.json existe
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: frontend/package.json no encontrado"
    exit 1
fi

# Verificar que next.config.js existe
if [ ! -f "frontend/next.config.js" ]; then
    echo "❌ Error: frontend/next.config.js no encontrado"
    exit 1
fi

# Verificar configuración de Vercel
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json no encontrado"
    exit 1
fi

echo "✅ Frontend verificado"

echo ""
echo "🔍 Verificando archivos de despliegue..."

# Verificar documentación
if [ ! -f "DEPLOY_STEPS.md" ]; then
    echo "⚠️  Advertencia: DEPLOY_STEPS.md no encontrado"
fi

echo "✅ Archivos verificados"

echo ""
echo "✅ ¡Pre-deployment verificado exitosamente!"
echo ""
echo "Próximo paso: Hacer push a main y los deploys se ejecutarán automáticamente"
