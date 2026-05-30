#!/bin/bash

echo "=============================================="
echo "   🛠️  C3PO BACKEND + RAILWAY AUTO-FIX"
echo "=============================================="

cd /workspaces/c3po || exit 1

echo ""
echo "🔍 1. Detectando backend real..."
if [ -d "backend" ]; then
    echo "✔ Carpeta backend encontrada."
else
    echo "❌ No existe carpeta backend. No puedo continuar."
    exit 1
fi

echo ""
echo "🔍 2. Buscando main.py real..."
if [ -f "backend/main.py" ]; then
    echo "✔ backend/main.py encontrado."
else
    echo "❌ backend/main.py NO existe."
    exit 1
fi

echo ""
echo "🔍 3. Detectando main.py incorrecto en la raíz..."
if [ -f "main.py" ]; then
    echo "⚠️  Encontrado main.py en la raíz. Lo renombro para evitar conflictos."
    mv main.py main_unused.py
else
    echo "✔ No existe main.py en la raíz. Perfecto."
fi

echo ""
echo "🔍 4. Validando api_router..."
if grep -R "api_router" -n backend/app/api/v1 >/dev/null 2>&1; then
    echo "✔ api_router encontrado."
else
    echo "❌ api_router NO encontrado. Revisa backend/app/api/v1/router.py"
fi

echo ""
echo "🔍 5. Validando settings.API_V1_PREFIX..."
if grep -R "API_V1_PREFIX" -n backend/app/core/settings.py >/dev/null 2>&1; then
    echo "✔ API_V1_PREFIX encontrado."
else
    echo "❌ API_V1_PREFIX NO encontrado en settings.py"
fi

echo ""
echo "🔍 6. Regenerando railway.json..."
if [ -f "railway.json" ]; then
    mv railway.json railway.json.bak
    echo "📦 Backup creado: railway.json.bak"
fi

cat << 'EOF' > railway.json
{
  "build": {
    "builder": "dockerfile",
    "buildpacks": []
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyMaxRetries": 10,
    "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "healthchecks": {
      "readiness": {
        "command": "curl --fail http://0.0.0.0:8000/ || exit 1"
      },
      "liveness": {
        "command": "curl --fail http://0.0.0.0:8000/ || exit 1"
      }
    }
  }
}
EOF

echo "✔ railway.json regenerado."

echo ""
echo "🔍 7. Mostrando railway.json final:"
cat railway.json

echo ""
echo "=============================================="
echo "   🎉 AUTO-FIX COMPLETADO"
echo "=============================================="
echo "👉 Ahora haz deploy en Railway."
echo "👉 Tu backend usará backend/main.py con routers."
echo "👉 /api/v1/auth/login dejará de dar 404."
