#!/bin/bash

echo "=============================================="
echo "   🧠 C3PO FULL SYSTEM HEALTH CHECK"
echo "=============================================="

BACKEND_URL_PROD="https://c3po-production-0c24.up.railway.app"
BACKEND_URL_DEV="http://localhost:8000"

echo ""
echo "🔍 1. Verificando variables de entorno en Vercel..."
echo "----------------------------------------------"
cd frontend
vercel env ls

echo ""
echo "🔍 2. Verificando .env.local..."
echo "----------------------------------------------"
if [ -f ".env.local" ]; then
    cat .env.local
else
    echo "❌ No existe .env.local"
fi

echo ""
echo "🔍 3. Probando conectividad con backend (PROD)..."
echo "----------------------------------------------"
curl -I "$BACKEND_URL_PROD" --max-time 5

echo ""
echo "🔍 4. Probando conectividad con backend (DEV)..."
echo "----------------------------------------------"
curl -I "$BACKEND_URL_DEV" --max-time 5

echo ""
echo "🔍 5. Probando endpoint /health (si existe)..."
echo "----------------------------------------------"
curl "$BACKEND_URL_PROD/health" --max-time 5

echo ""
echo "🔍 6. Probando endpoint /api/v1 (si existe)..."
echo "----------------------------------------------"
curl "$BACKEND_URL_PROD/api/v1" --max-time 5

echo ""
echo "🔍 7. Probando CORS..."
echo "----------------------------------------------"
curl -I -H "Origin: https://c3po.vercel.app" "$BACKEND_URL_PROD" --max-time 5

echo ""
echo "🔍 8. Probando autenticación (si aplica)..."
echo "----------------------------------------------"
curl -X POST "$BACKEND_URL_PROD/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"123456"}' \
    --max-time 5

echo ""
echo "🔍 9. Probando Axios desde Node..."
echo "----------------------------------------------"
node <<EOF
import axios from "axios";

const url = "$BACKEND_URL_PROD/api/v1";
console.log("Probando Axios →", url);

axios.get(url)
  .then(res => console.log("✔ Axios OK:", res.status))
  .catch(err => console.error("❌ Axios ERROR:", err.message));
EOF

echo ""
echo "=============================================="
echo "   🎉 HEALTH CHECK COMPLETADO"
echo "=============================================="
