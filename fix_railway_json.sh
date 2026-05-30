#!/bin/bash

echo "=============================================="
echo "   🔧 FIX RAILWAY.JSON – C3PO BACKEND"
echo "=============================================="

# 1. Ir a la raíz del repo
cd /workspaces/c3po || exit 1

# 2. Si existe railway.json, hacer backup
if [ -f "railway.json" ]; then
    echo "📦 Haciendo backup de railway.json existente..."
    mv railway.json railway.json.bak
else
    echo "✔ No existe railway.json previo, creando uno nuevo..."
fi

# 3. Crear railway.json correcto
echo "🛠 Generando railway.json limpio..."

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
    "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port 8000",
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

echo "=============================================="
echo "   🎉 railway.json REGENERADO CORRECTAMENTE"
echo "=============================================="
echo "Contenido final:"
cat railway.json

echo ""
echo "👉 Ahora haz deploy en Railway para aplicar los cambios."
echo "👉 Si usas Dockerfile, asegúrate de que expone el puerto 8000."
