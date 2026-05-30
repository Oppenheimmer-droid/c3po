#!/bin/bash

echo "=============================================="
echo "   🧠 BACKEND FASTAPI DIAGNOSTIC TOOL"
echo "=============================================="

BACKEND_URL="https://c3po-production-0c24.up.railway.app"

echo ""
echo "🔍 1. Probando raíz del backend..."
curl -I "$BACKEND_URL" --max-time 5

echo ""
echo "🔍 2. Probando /docs..."
curl -I "$BACKEND_URL/docs" --max-time 5

echo ""
echo "🔍 3. Probando /openapi.json..."
curl -I "$BACKEND_URL/openapi.json" --max-time 5

echo ""
echo "🔍 4. Probando /api/v1..."
curl -I "$BACKEND_URL/api/v1" --max-time 5

echo ""
echo "🔍 5. Probando rutas comunes..."
for route in "users" "auth/login" "auth/register" "items" "health"; do
  echo "→ Probando /api/v1/$route"
  curl -I "$BACKEND_URL/api/v1/$route" --max-time 5
done

echo ""
echo "=============================================="
echo "   🔍 ANALIZANDO RESULTADOS"
echo "=============================================="

echo "Si /openapi.json devuelve 404 → FastAPI no está cargando routers."
echo "Si /docs devuelve 404 → FastAPI no está montado correctamente."
echo "Si /api/v1/* devuelve 404 → falta include_router() o prefix incorrecto."
echo "Si raíz devuelve 405 → servidor vivo pero sin rutas montadas."
echo ""
echo "=============================================="
echo "   🎉 DIAGNÓSTICO COMPLETADO"
echo "=============================================="

