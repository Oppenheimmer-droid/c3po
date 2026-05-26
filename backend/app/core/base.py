from sqlalchemy.orm import declarative_base

# Declarative base separado para evitar crear engines en tiempo de import
Base = declarative_base()
