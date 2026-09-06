from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    purchase_price = Column(Float) # Precio pagado individualmente
    status = Column(String, default="available") # available / assembled / sold
    
    # Relación con el PC en el que se monte
    assembled_pc_id = Column(Integer, ForeignKey("assembled_pcs.id"), nullable=True)

class AssembledPC(Base):
    __tablename__ = "assembled_pcs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # Nombre del proyecto (ej: "Gaming Pro 1")
    sale_price = Column(Float, default=0.0) # Por cuánto se vendió
    total_cost = Column(Float, default=0.0) # Suma de los purchase_price de sus piezas
    is_sold = Column(Boolean, default=False)
    
    components = relationship("Component", backref="pc")