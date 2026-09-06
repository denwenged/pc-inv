from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, auth, database
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Crea las tablas en la base de datos al arrancar
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de CORS para que el frontend pueda hablar con el backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción podrías poner la IP de tu ZimaOS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RUTAS DE USUARIO Y SEGURIDAD ---

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    # Comprobar si el usuario ya existe
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed = auth.get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return {"message": "Usuario creado correctamente"}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"token": access_token, "type": "bearer"}

# --- RUTAS DE INVENTARIO (COMPONENTES) ---

@app.post("/components/add-bulk")
def add_bulk(name: str, category: str, quantity: int, price_per_unit: float, db: Session = Depends(get_db)):
    """Añade varios componentes iguales, cada uno con su propio registro de precio"""
    for _ in range(quantity):
        item = models.Component(name=name, category=category, purchase_price=price_per_unit)
        db.add(item)
    db.commit()
    return {"message": f"Se han añadido {quantity} unidades de {name}"}

@app.post("/components/add-bundle")
def add_bundle(names: List[str], total_price: float, db: Session = Depends(get_db)):
    """Añade un pack de piezas y divide el coste total entre ellas"""
    if not names:
        raise HTTPException(status_code=400, detail="La lista de nombres está vacía")
    
    price_each = total_price / len(names)
    for name in names:
        item = models.Component(name=name, category="Bundle Item", purchase_price=price_each)
        db.add(item)
    db.commit()
    return {"message": "Bundle añadido y precio repartido equitativamente"}

@app.get("/components/available")
def get_available_components(db: Session = Depends(get_db)):
    """Lista solo los componentes que están en stock (no montados)"""
    return db.query(models.Component).filter(models.Component.status == "available").all()

# --- RUTAS DE MONTAJE Y VENTAS ---

@app.post("/pc/assemble")
def assemble_pc(pc_name: str, component_ids: List[int], db: Session = Depends(get_db)):
    """Crea un PC a partir de componentes seleccionados del stock"""
    items = db.query(models.Component).filter(models.Component.id.in_(component_ids)).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="No se seleccionaron componentes válidos")

    # Calculamos el coste total del PC sumando lo que pagaste por cada pieza
    coste_total_pc = sum(item.purchase_price for item in items)
    
    nuevo_pc = models.AssembledPC(name=pc_name, total_cost=coste_total_pc)
    db.add(nuevo_pc)
    db.flush() # Para obtener el ID del PC antes del commit final
    
    # Marcamos los componentes como usados en este PC
    for item in items:
        item.status = "assembled"
        item.assembled_pc_id = nuevo_pc.id
    
    db.commit()
    return {"message": "PC Montado con éxito", "id": nuevo_pc.id, "coste_total": coste_total_pc}

@app.get("/pcs-all")
def get_all_pcs(db: Session = Depends(get_db)):
    """Lista todos los PCs montados (vendidos y no vendidos)"""
    return db.query(models.AssembledPC).all()

@app.post("/pc/sell/{pc_id}")
def sell_pc(pc_id: int, final_price: float, db: Session = Depends(get_db)):
    """Marca un PC como vendido y calcula el beneficio"""
    pc = db.query(models.AssembledPC).filter(models.AssembledPC.id == pc_id).first()
    if not pc:
        raise HTTPException(status_code=404, detail="PC no encontrado")
    
    pc.sale_price = final_price
    pc.is_sold = True
    pc.profit = final_price - pc.total_cost # Beneficio neto
    
    db.commit()
    return {
        "status": "Vendido",
        "beneficio_neto": pc.profit,
        "coste_total": pc.total_cost
    }