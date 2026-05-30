#!/bin/bash

echo "=============================================="
echo "   🚀 VERCEL FRONTEND FIX – SCRIPT MAESTRO"
echo "=============================================="

# 1. Verificar carpeta frontend
if [ ! -d "frontend" ]; then
    echo "❌ No se encontró la carpeta 'frontend'."
    echo "   Ejecuta este script desde /workspaces/c3po"
    exit 1
fi

cd frontend
echo "📁 Directorio actual: $(pwd)"

# 2. Limpiar .vercel si está corrupto
if [ -d ".vercel" ]; then
    echo "🧹 Eliminando .vercel previo para evitar links corruptos..."
    rm -rf .vercel
else
    echo "✔ No existe .vercel previo, limpio."
fi

# 3. Linkear proyecto
echo "🔗 Linkeando proyecto frontend..."
vercel link --yes >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Error al linkear. Ejecuta manualmente: vercel link"
    exit 1
fi

echo "✔ Proyecto linkeado correctamente."

# 4. Mostrar variables actuales
echo "🔍 Variables actuales:"
vercel env ls

# 5. Función para añadir variable si falta
add_if_missing() {
    ENV=$1
    VALUE=$2

    if vercel env ls | grep -q "$ENV"; then
        echo "✔ NEXT_PUBLIC_API_URL ya existe en $ENV"
    else
        echo "➕ Añadiendo NEXT_PUBLIC_API_URL a $ENV..."
        printf "%s" "$VALUE" | vercel env add NEXT_PUBLIC_API_URL "$ENV"
    fi
}

echo "=============================================="
echo "   ➕ Añadiendo variables si faltan"
echo "=============================================="

# Development
add_if_missing "Development" "http://localhost:8000"

# Production
add_if_missing "Production" "https://c3po-production-0c24.up.railway.app"

# Preview
add_if_missing "Preview" "https://c3po-production-0c24.up.railway.app"

echo "=============================================="
echo "   🔍 Variables finales:"
echo "=============================================="
vercel env ls

echo "=============================================="
echo "   📥 Pull de variables a .env.local"
echo "=============================================="
vercel env pull .env.local --yes

echo "=============================================="
echo "   🎉 TODO LISTO – ENTORNO VERCEL PERFECTO"
echo "=============================================="

