#!/usr/bin/env python3
"""
Script para inicializar la base de datos.
Crea todas las tablas y el tenant por defecto.
"""
import asyncio
import json
import sys
from pathlib import Path

# Agregar el directorio app al path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import _get_engine, _get_session_local
from app.models import Base, Tenant, TenantStatus


async def init_database():
    """Inicializa la base de datos creando tablas y datos iniciales."""
    print("🔧 Inicializando base de datos...")
    
    engine = _get_engine()
    session_local = _get_session_local()
    
    # Crear todas las tablas
    print("📋 Creando tablas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas creadas")
    
    # Crear tenant por defecto si no existe
    print("🏢 Verificando tenant por defecto...")
    async with session_local() as session:
        result = await session.execute(
            text("SELECT id FROM tenants WHERE slug = 'default'")
        )
        existing = result.fetchone()
        
        if not existing:
            # El campo settings es Text (VARCHAR), necesita JSON serializado
            settings_json = json.dumps({
                "theme": "light",
                "features": {
                    "chat": True,
                    "documents": True,
                    "evaluations": True,
                }
            })
            
            default_tenant = Tenant(
                name="Default Organization",
                slug="default",
                status=TenantStatus.ACTIVE,
                settings=settings_json
            )
            session.add(default_tenant)
            await session.commit()
            print("✅ Tenant por defecto creado")
        else:
            print("ℹ️  Tenant por defecto ya existe")
    
    await engine.dispose()
    print("🎉 Base de datos inicializada correctamente!")


if __name__ == "__main__":
    asyncio.run(init_database())
