import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------
# PATH correcto para que Alembic encuentre app/
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ---------------------------------------------------------
# Importar Base desde app.models
# ---------------------------------------------------------
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------
# Metadata de los modelos
# ---------------------------------------------------------
target_metadata = Base.metadata

# ---------------------------------------------------------
# Fix para URLs postgres:// → postgresql://
# ---------------------------------------------------------
def fix_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

# ---------------------------------------------------------
# Modo offline
# ---------------------------------------------------------
def run_migrations_offline():
    url = fix_url(config.get_main_option("sqlalchemy.url"))
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ---------------------------------------------------------
# Modo online
# ---------------------------------------------------------
def run_migrations_online():
    section = config.get_section(config.config_ini_section)
    section["sqlalchemy.url"] = fix_url(section["sqlalchemy.url"])

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
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
