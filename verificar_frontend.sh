#!/bin/bash

FRONTEND_URL="https://frontend-pi-seven-18.vercel.app"
BACKEND_URL="https://c3po-production-0c24.up.railway.app"

echo "🔍 Verificando estado del FRONTEND..."
echo "----------------------------------------"
curl -I "$FRONTEND_URL"
echo

echo "🔍 Verificando si el FRONTEND expone /api/v1/subjects (NO debería)..."
echo "----------------------------------------"
curl -v "$FRONTEND_URL/api/v1/subjects" 2>&1 | sed 's/^/    /'
echo

echo "🔍 Verificando si el BACKEND responde correctamente..."
echo "----------------------------------------"
curl -v "$BACKEND_URL/api/v1/subjects" 2>&1 | sed 's/^/    /'
echo

echo "🔍 Test de conexión FRONTEND → BACKEND simulando fetch..."
echo "----------------------------------------"
curl -H "Origin: $FRONTEND_URL" -v "$BACKEND_URL/api/v1/subjects" 2>&1 | sed 's/^/    /'
echo

echo "🔍 Verificando CORS..."
echo "----------------------------------------"
curl -H "Origin: $FRONTEND_URL" -I "$BACKEND_URL/api/v1/subjects"
echo

echo "🔍 Verificando si el FRONTEND está usando NEXT_PUBLIC_API_URL..."
echo "----------------------------------------"

grep -RIl --exclude-dir=node_modules -E "NEXT_PUBLIC_API_URL" ../frontend 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ No se encontró uso de NEXT_PUBLIC_API_URL en el frontend."
else
    echo "✅ El frontend usa NEXT_PUBLIC_API_URL."
fi

echo
echo "🔍 Verificando llamadas fetch/axios incorrectas..."
echo "----------------------------------------"

grep -RIn --exclude-dir=node_modules -E "fetch\(|axios\(" ../frontend 2>/dev/null | sed 's/^/    /'

echo
echo "🎯 RESULTADOS ESPERADOS:"
echo "----------------------------------------"
echo "✔ FRONTEND / debe devolver HTML"
echo "✔ FRONTEND /api/v1/subjects debe devolver 404 (correcto)"
echo "✔ BACKEND /api/v1/subjects debe devolver JSON"
echo "✔ Test CORS debe mostrar Access-Control-Allow-Origin: *"
echo "✔ Si el frontend no usa NEXT_PUBLIC_API_URL → ERROR"
echo "✔ Si fetch apunta a /api/... → ERROR"
echo
echo "🎉 Verificación completada."
