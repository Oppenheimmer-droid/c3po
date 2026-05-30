#!/bin/bash

echo "=============================================="
echo "   🔧 FIX VERCEL ENV – FRONTEND CLEANUP"
echo "=============================================="

# 1. Moverse a la carpeta frontend
if [ ! -d "frontend" ]; then
    echo "❌ No se encontró la carpeta 'frontend'."
    echo "   Ejecuta este script desde /workspaces/c3po"
    exit 1
fi

cd frontend
echo "📁 Directorio actual: $(pwd)"

# 2. Verificar si está linkeado
echo "🔍 Verificando si el proyecto está linkeado..."
if ! vercel link --confirm >/dev/null 2>&1; then
    echo "❌ El proyecto no está linkeado."
    echo "🔗 Ejecutando link automático..."
    vercel link
else
    echo "✅ Proyecto ya linkeado correctamente."
fi

# 3. Mostrar variables actuales
echo "🔍 Variables actuales:"
vercel env ls

# 4. Función para añadir variable si falta
add_if_missing() {
    ENV=$1
    VALUE=$2

    if vercel env ls | grep -q "$ENV"; then
        echo "✔ $ENV ya existe, no se añade."
    else
        echo "➕ Añadiendo $ENV..."
        printf "%s" "$VALUE" | vercel env add NEXT_PUBLIC_API_URL "$ENV"
    fi
}

echo "=============================================="
echo "   ➕ Añadiendo variables si faltan"
echo "=============================================="

# Añadir Development
add_if_missing "Development" "http://localhost:8000"

# Añadir Production
add_if_missing "Production" "https://c3po-production-0c24.up.railway.app"

# Añadir Preview
add_if_missing "Preview" "https://c3po-production-0c24.up.railway.app"

echo "=============================================="
echo "   🔍 Variables finales:"
echo "=============================================="
vercel env ls

echo "=============================================="
echo "   📥 Haciendo pull a .env.local"
echo "=============================================="
vercel env pull .env.local --yes

echo "=============================================="
echo "   🎉 TODO LISTO – VARIABLES CONFIGURADAS"
echo "=============================================="
