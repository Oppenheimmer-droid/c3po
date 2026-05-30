#!/usr/bin/env bash
set -e

echo "==============================================="
echo " VALIDACIÓN COMPLETA DEL BACKEND MULTI‑TENANT "
echo "==============================================="

echo ""
echo "=== 1. Verificando duplicados de Tenant ==="
grep -R "class Tenant" -n backend/app || true
grep -R "__tablename__ = \"tenants\"" -n backend/app || true

echo ""
echo "=== 2. Verificando imports de Tenant ==="
grep -R "import Tenant" -n backend/app || true

echo ""
echo "=== 3. Verificando que tenant_repository usa el Tenant correcto ==="
grep -n "from app.models.auth import Tenant" backend/app/repositories/tenant_repository.py || \
echo "❌ tenant_repository.py NO usa el Tenant correcto"

echo ""
echo "=== 4. Verificando que models/__init__.py importa el Tenant correcto ==="
grep -n "from app.models.auth import Tenant" backend/app/models/__init__.py || \
echo "❌ models/__init__.py NO importa el Tenant correcto"

echo ""
echo "=== 5. Verificando que NO existe backend/app/models/tenant.py ==="
if [ -f backend/app/models/tenant.py ]; then
    echo "❌ ERROR: backend/app/models/tenant.py todavía existe"
else
    echo "✔ OK: backend/app/models/tenant.py eliminado"
fi

echo ""
echo "=== 6. Verificando chat.py (imports correctos) ==="
grep -n "from app.core.tenant import TenantContext, get_tenant_context" backend/app/api/v1/chat.py || \
echo "❌ chat.py NO tiene el import correcto"

echo ""
echo "=== 7. Verificando que no hay basura pegada en chat.py ==="
grep -n "}from app.core.tenant" backend/app/api/v1/chat.py && \
echo "❌ chat.py contiene basura" || echo "✔ OK: chat.py limpio"

echo ""
echo "=== 8. Verificando vector_store.py ==="
if grep -q "def retrieval_pipeline" backend/app/rag/vector_store.py; then
    echo "✔ vector_store.py correcto"
else
    echo "❌ vector_store.py incompleto"
fi

echo ""
echo "=== 9. Verificando estructura de modelos ==="
grep -R "__tablename__" -n backend/app/models || true

echo ""
echo "=== 10. Verificando dependencias rotas (import errors) ==="
python3 - << 'EOF'
import pkgutil, sys

print("→ Escaneando imports de backend/app ...")
for importer, modname, ispkg in pkgutil.walk_packages(path=['backend/app'], prefix='app.'):
    try:
        __import__(modname)
    except Exception as e:
        print(f"❌ ERROR importando {modname}: {e}")
EOF

echo ""
echo "==============================================="
echo " VALIDACIÓN COMPLETADA "
echo " Si todo está en ✔, ejecuta: railway up"
echo "==============================================="
