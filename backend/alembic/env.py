import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# ---------------------------------------------------------
# Ajustar PATH para que Alembic encuentre app/
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ---------------------------------------------------------
# Importar settings y Base
# ---------------------------------------------------------
from app.core.config import settings
from app.models import Base

# ---------------------------------------------------------
# Configuración Alembic
# ---------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ---------------------------------------------------------
# Obtener URL real o dummy
# ---------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", None)

if not DATABASE_URL:
    print("⚠️ WARNING: DATABASE_URL no encontrado. Usando dummy sqlite.")
    DATABASE_URL = "sqlite:///./dummy.db"

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ---------------------------------------------------------
# Funciones de ejecución
# ---------------------------------------------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
