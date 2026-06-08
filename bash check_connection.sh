#!/usr/bin/env bash
# ============================================================
# check_connection.sh — Verifica toda la cadena Vercel→Railway
# Ejecutar desde cualquier sitio: bash check_connection.sh
# ============================================================

# ── Config — edita estas dos líneas si tus URLs son distintas ─
BACKEND="https://c3po-production-0c24.up.railway.app"
FRONTEND="https://c3po-frontend.vercel.app"
TENANT_SLUG="default"
EMAIL="admin@demo.com"
PASSWORD="admin123"
# ─────────────────────────────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; GRAY='\033[0;90m'; NC='\033[0m'

PASS=0; FAIL=0

ok()   { echo -e "  ${GREEN}✓${NC} $1"; ((PASS++)); }
fail() { echo -e "  ${RED}✗${NC} $1"; ((FAIL++)); }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
info() { echo -e "  ${BLUE}→${NC} $1"; }
dim()  { echo -e "  ${GRAY}$1${NC}"; }
sep()  { echo -e "\n${BOLD}[$1]${NC} $2"; }

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   C3PO Connection Check — Railway+Vercel ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo -e "  Backend:  ${BLUE}$BACKEND${NC}"
echo -e "  Frontend: ${BLUE}$FRONTEND${NC}"
echo ""

# ════════════════════════════════════════════════════════════
sep "1/7" "Backend vivo (health check)"
# ════════════════════════════════════════════════════════════
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" \
  --max-time 10 "$BACKEND/api/v1/health")

if [ "$HEALTH" = "200" ]; then
  ok "GET /api/v1/health → 200"
else
  fail "GET /api/v1/health → $HEALTH (esperado 200)"
  warn "El backend no está respondiendo. Revisa los logs de Railway."
  echo ""
  echo -e "${RED}${BOLD}Abortando — sin backend no hay nada que comprobar.${NC}"
  exit 1
fi

# Mostrar detalle del health
HEALTH_BODY=$(curl -s --max-time 10 "$BACKEND/api/v1/health")
dim "  Respuesta: $HEALTH_BODY"

# ════════════════════════════════════════════════════════════
sep "2/7" "CORS preflight (OPTIONS desde origen Vercel)"
# ════════════════════════════════════════════════════════════
CORS_HEADERS=$(curl -s -o /dev/null -D - \
  --max-time 10 \
  -X OPTIONS "$BACKEND/api/v1/auth/login" \
  -H "Origin: $FRONTEND" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization,X-Tenant-Slug")

CORS_STATUS=$(echo "$CORS_HEADERS" | grep "HTTP" | tail -1 | awk '{print $2}')
CORS_ORIGIN=$(echo "$CORS_HEADERS" | grep -i "access-control-allow-origin" | tr -d '\r')
CORS_CREDS=$(echo  "$CORS_HEADERS" | grep -i "access-control-allow-credentials" | tr -d '\r')

if [[ "$CORS_STATUS" == "200" || "$CORS_STATUS" == "204" ]]; then
  ok "Preflight OPTIONS → $CORS_STATUS"
else
  fail "Preflight OPTIONS → $CORS_STATUS (esperado 200/204)"
  warn "CORSMiddleware no responde. ¿Se aplicó el fix de main.py?"
fi

if echo "$CORS_ORIGIN" | grep -qi "$FRONTEND\|*"; then
  ok "Access-Control-Allow-Origin: $FRONTEND"
else
  fail "Access-Control-Allow-Origin ausente o incorrecto"
  dim "  Recibido: $CORS_ORIGIN"
  warn "Revisa CORS_ORIGINS en Railway Variables → URL exacta sin wildcards"
fi

if echo "$CORS_CREDS" | grep -qi "true"; then
  ok "Access-Control-Allow-Credentials: true"
else
  fail "Access-Control-Allow-Credentials ausente"
  dim "  Recibido: $CORS_CREDS"
fi

# ════════════════════════════════════════════════════════════
sep "3/7" "Login (POST /auth/login con X-Tenant-Slug)"
# ════════════════════════════════════════════════════════════
LOGIN_RESP=$(curl -s --max-time 15 \
  -X POST "$BACKEND/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $FRONTEND" \
  -H "X-Tenant-Slug: $TENANT_SLUG" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

LOGIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  --max-time 15 \
  -X POST "$BACKEND/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $FRONTEND" \
  -H "X-Tenant-Slug: $TENANT_SLUG" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo "$LOGIN_RESP" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null || echo "")

if [ "$LOGIN_STATUS" = "200" ] && [ -n "$ACCESS_TOKEN" ]; then
  ok "Login → 200 · token recibido"
  dim "  Token (primeros 40 chars): ${ACCESS_TOKEN:0:40}..."
elif [ "$LOGIN_STATUS" = "401" ]; then
  fail "Login → 401 Unauthorized"
  warn "Credenciales incorrectas o tenant no encontrado."
  warn "¿Se aplicó el fix X-Tenant-Slug en auth.service.ts?"
  dim "  Respuesta: $LOGIN_RESP"
elif [ "$LOGIN_STATUS" = "404" ]; then
  fail "Login → 404 Not Found"
  warn "El endpoint /auth/login no está montado."
  warn "¿Se aplicó el fix de main.py (api_router)?"
elif [ "$LOGIN_STATUS" = "422" ]; then
  fail "Login → 422 Unprocessable Entity"
  warn "El body del request no tiene el formato esperado."
  dim "  Respuesta: $LOGIN_RESP"
else
  fail "Login → $LOGIN_STATUS"
  dim "  Respuesta: $LOGIN_RESP"
fi

# ════════════════════════════════════════════════════════════
sep "4/7" "Token válido (GET /auth/me)"
# ════════════════════════════════════════════════════════════
if [ -z "$ACCESS_TOKEN" ]; then
  warn "Sin token — saltando test /auth/me"
else
  ME_RESP=$(curl -s --max-time 10 \
    "$BACKEND/api/v1/auth/me" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Origin: $FRONTEND")

  ME_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 10 \
    "$BACKEND/api/v1/auth/me" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Origin: $FRONTEND")

  ME_EMAIL=$(echo "$ME_RESP" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null || echo "")

  if [ "$ME_STATUS" = "200" ] && [ -n "$ME_EMAIL" ]; then
    ok "GET /auth/me → 200"
    dim "  Usuario: $ME_EMAIL"
    ROLE=$(echo "$ME_RESP" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d.get('role','?'))" 2>/dev/null || echo "?")
    TENANT=$(echo "$ME_RESP" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d.get('tenant_id','?'))" 2>/dev/null || echo "?")
    dim "  Rol: $ROLE | Tenant ID: $TENANT"
  elif [ "$ME_STATUS" = "401" ]; then
    fail "GET /auth/me → 401 (token rechazado)"
    warn "SECRET_KEY puede ser distinta entre deploys. Verifica en Railway Variables."
  else
    fail "GET /auth/me → $ME_STATUS"
    dim "  Respuesta: $ME_RESP"
  fi
fi

# ════════════════════════════════════════════════════════════
sep "5/7" "Base de datos accesible (endpoint protegido)"
# ════════════════════════════════════════════════════════════
if [ -z "$ACCESS_TOKEN" ]; then
  warn "Sin token — saltando test de BD"
else
  DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 10 \
    "$BACKEND/api/v1/documents" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Origin: $FRONTEND")

  if [[ "$DOCS_STATUS" == "200" || "$DOCS_STATUS" == "404" ]]; then
    ok "GET /documents → $DOCS_STATUS (BD conectada)"
  elif [ "$DOCS_STATUS" = "500" ]; then
    fail "GET /documents → 500 (error interno — posible fallo de BD)"
    warn "Revisa DATABASE_URL en Railway Variables."
    warn "La URL debe ser: postgresql+asyncpg://... o postgresql://..."
  elif [ "$DOCS_STATUS" = "503" ]; then
    fail "GET /documents → 503 (BD no disponible)"
    warn "PostgreSQL puede estar arrancando. Espera 30s y reintenta."
  else
    fail "GET /documents → $DOCS_STATUS"
  fi
fi

# ════════════════════════════════════════════════════════════
sep "6/7" "Frontend Vercel accesible"
# ════════════════════════════════════════════════════════════
FE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  --max-time 15 "$FRONTEND")

if [ "$FE_STATUS" = "200" ]; then
  ok "Frontend → 200"
else
  fail "Frontend → $FE_STATUS"
  warn "El deploy de Vercel puede tener errores de build."
fi

# ════════════════════════════════════════════════════════════
sep "7/7" "Variable NEXT_PUBLIC_API_URL apunta al backend correcto"
# ════════════════════════════════════════════════════════════
# Buscar la URL del API en el HTML del frontend (Next.js la incrusta en build)
FE_HTML=$(curl -s --max-time 15 "$FRONTEND" 2>/dev/null || echo "")
BACKEND_DOMAIN=$(echo "$BACKEND" | sed 's|https://||')

if echo "$FE_HTML" | grep -q "$BACKEND_DOMAIN"; then
  ok "Frontend referencia al backend correcto ($BACKEND_DOMAIN)"
else
  warn "No se detectó la URL del backend en el HTML del frontend"
  warn "Verifica NEXT_PUBLIC_API_URL en Vercel → Settings → Environment Variables"
  dim "  Valor esperado: $BACKEND"
fi

# ════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ════════════════════════════════════════════════════════════
TOTAL=$((PASS + FAIL))
echo ""
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo -e "${BOLD}  Resultado: ${GREEN}$PASS${NC}${BOLD} passed · ${RED}$FAIL${NC}${BOLD} failed · $TOTAL total${NC}"
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}${BOLD}  ✓ Todo OK — el login desde Vercel a Railway debería funcionar.${NC}"
else
  echo -e "${RED}${BOLD}  ✗ Hay $FAIL problema(s). Guía rápida:${NC}"
  echo ""
  echo -e "  ${BOLD}502 en health${NC}       → app no arranca, revisa logs Railway"
  echo -e "  ${BOLD}CORS falla${NC}          → main.py sin CORSMiddleware o CORS_ORIGINS con wildcard"
  echo -e "  ${BOLD}Login 404${NC}           → api_router no montado en main.py"
  echo -e "  ${BOLD}Login 401${NC}           → header X-Tenant-ID en vez de X-Tenant-Slug"
  echo -e "  ${BOLD}Login 500${NC}           → DATABASE_URL mal formada o psycopg crash"
  echo -e "  ${BOLD}/auth/me 401${NC}        → SECRET_KEY distinta entre deploys"
  echo -e "  ${BOLD}NEXT_PUBLIC_API_URL${NC} → configurarla en Vercel Environment Variables"
fi
echo ""