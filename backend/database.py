# backend/database.py completo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usamos postgresql+psycopg2 para ser explícitos
# Y nos aseguramos de que la URL termine en /pc_inventario (con barra)
default_url = "postgresql+psycopg2://admin:admin_password_123@db-pc:5432/pc_inventario"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default_url)

# Si por algún motivo la URL viene mal del env, intentamos arreglarla
if SQLALCHEMY_DATABASE_URL and "@db-pc:pc_inventario" in SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("@db-pc:pc_inventario", "@db-pc/pc_inventario")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()