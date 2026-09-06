from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# La URL se construye con los datos que pondremos en el docker-compose
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db/inventario")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()