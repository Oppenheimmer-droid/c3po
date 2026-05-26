#!/usr/bin/env bash

# Script generalizado para build y deploy del proyecto
# - Construye frontend (Next.js)
# - Ejecuta tests y empaqueta backend
# - Construye imagen Docker opcional y la sube a un registry opcional
# - Lanza despliegue con `vercel` (frontend) y `railway` (backend) si están disponibles

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"

IMAGE_NAME="c3po-backend:latest"
REGISTRY="" # e.g. ghcr.io/owner/repo or registry.example.com/owner/repo
PUSH_IMAGE=false

usage() {
  cat <<EOF
Usage: $0 [--push-registry <registry>] [--image-name <name>] [--no-railway] [--no-vercel]

Options:
  --push-registry <registry>  Push Docker image to given registry (will tag and push)
  --image-name <name>         Custom docker image name (default: ${IMAGE_NAME})
  --no-railway                Skip Railway deploy step
  --no-vercel                 Skip Vercel deploy step
  -h, --help                  Show this help
EOF
}

NO_RAILWAY=false
NO_VERCEL=false

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --push-registry)
      REGISTRY="$2"; PUSH_IMAGE=true; shift 2;;
    --image-name)
      IMAGE_NAME="$2"; shift 2;;
    --no-railway)
      NO_RAILWAY=true; shift;;
    --no-vercel)
      NO_VERCEL=true; shift;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

echo "==> Build y deploy generalizado"

# 1) Frontend build
if [ -d "$FRONTEND_DIR" ] && [ "$NO_VERCEL" = false ]; then
  echo "-> Construyendo frontend en $FRONTEND_DIR"
  if command -v npm >/dev/null 2>&1; then
    pushd "$FRONTEND_DIR" >/dev/null
    npm ci
    npm run build
    popd >/dev/null
  else
    echo "npm no encontrado — saltando build frontend (instala Node/npm)"
  fi
else
  echo "-> Omitiendo build frontend"
fi

# 2) Backend tests y checks
if [ -d "$BACKEND_DIR" ]; then
  echo "-> Preparando backend en $BACKEND_DIR"
  if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
    # Usa el venv del repo si existe
    source "$ROOT_DIR/.venv/bin/activate"
  fi

  pushd "$BACKEND_DIR" >/dev/null
  if command -v pip >/dev/null 2>&1; then
    pip install -r requirements.txt || true
  fi
  if command -v pytest >/dev/null 2>&1; then
    PYTHONPATH="$BACKEND_DIR" pytest -q || echo "Tests fallaron — revisa salida";
  else
    echo "pytest no encontrado — saltando tests"
  fi
  popd >/dev/null
else
  echo "No se encontró carpeta backend — saltando paso"
fi

# 3) Build Docker image (backend)
if command -v docker >/dev/null 2>&1 && [ -d "$BACKEND_DIR" ]; then
  echo "-> Construyendo imagen Docker para backend"
  pushd "$BACKEND_DIR" >/dev/null
  docker build -t "$IMAGE_NAME" -f Dockerfile .
  popd >/dev/null

  if [ "$PUSH_IMAGE" = true ]; then
    if [ -z "$REGISTRY" ]; then
      echo "Registry no especificado. Use --push-registry <registry>"; exit 1
    fi
    TAG="$REGISTRY:$(date +%Y%m%d%H%M%S)"
    docker tag "$IMAGE_NAME" "$TAG"
    docker push "$TAG"
    echo "Imagen empujada: $TAG"
  fi
else
  echo "Docker no disponible o no está el backend — saltando build de imagen"
fi

# 4) Run Alembic migrations locally (opcional)
if command -v alembic >/dev/null 2>&1 && [ -d "$BACKEND_DIR" ]; then
  echo "-> Ejecutando migraciones alembic (local)"
  pushd "$BACKEND_DIR" >/dev/null
  alembic upgrade head || echo "Alembic falló o no configurado"
  popd >/dev/null
else
  echo "alembic no disponible o no configurado — saltando migraciones locales"
fi

# 5) Trigger deploys
if [ "$NO_VERCEL" = false ]; then
  if command -v vercel >/dev/null 2>&1; then
    echo "-> Deploy frontend con Vercel"
    pushd "$FRONTEND_DIR" >/dev/null
    vercel --prod || echo "Vercel deploy falló — revisa token o login"
    popd >/dev/null
  else
    echo "Vercel CLI no encontrado — si usas Vercel, instala 'vercel' o haz deploy manual"
  fi
fi

if [ "$NO_RAILWAY" = false ]; then
  if command -v railway >/dev/null 2>&1; then
    echo "-> Deploy backend con Railway"
    pushd "$BACKEND_DIR" >/dev/null
    railway up --detach || echo "railway up falló — revisa el CLI o el login"
    popd >/dev/null
  else
    echo "Railway CLI no encontrado — si usas Railway, instala 'railway' o haz deploy manual"
  fi
fi

echo "==> Build y deploy finalizado (verifica dashboards de tus servicios)"

exit 0
