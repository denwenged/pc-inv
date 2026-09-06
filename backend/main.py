# backend/main.py completo
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, auth, database
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    # Leemos de las variables de entorno
    env_admin = os.getenv("ADMIN_USER", "admin")
    env_pass = os.getenv("ADMIN_PASSWORD", "admin1234")
    
    admin_exists = db.query(models.User).filter(models.User.username == env_admin).first()
    if not admin_exists:
        hashed_pw = auth.get_password_hash(env_pass)
        new_admin = models.User(username=env_admin, hashed_password=hashed_pw, is_admin=True)
        db.add(new_admin)
        db.commit()
    db.close()

# --- RUTAS --- (Mantenemos las anteriores)
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Error")
    return {"token": auth.create_access_token(data={"sub": user.username}), "type": "bearer"}

@app.get("/components/available")
def get_available(db: Session = Depends(get_db)):
    return db.query(models.Component).filter(models.Component.status == "available").all()

@app.post("/components/add-bulk")
def add_bulk(name: str, category: str, quantity: int, price_per_unit: float, db: Session = Depends(get_db)):
    for _ in range(quantity):
        db.add(models.Component(name=name, category=category, purchase_price=price_per_unit))
    db.commit()
    return {"message": "Añadidos"}

@app.post("/components/add-bundle")
def add_bundle(names: List[str], total_price: float, db: Session = Depends(get_db)):
    price_each = total_price / len(names)
    for name in names:
        db.add(models.Component(name=name, category="Bundle Item", purchase_price=price_each))
    db.commit()
    return {"message": "Bundle añadido"}

@app.post("/pc/assemble")
def assemble_pc(pc_name: str, component_ids: List[int], db: Session = Depends(get_db)):
    items = db.query(models.Component).filter(models.Component.id.in_(component_ids)).all()
    cost = sum(i.purchase_price for i in items)
    new_pc = models.AssembledPC(name=pc_name, total_cost=cost)
    db.add(new_pc)
    db.flush()
    for i in items:
        i.status = "assembled"
        i.assembled_pc_id = new_pc.id
    db.commit()
    return {"id": new_pc.id}

@app.get("/pcs-all")
def get_pcs(db: Session = Depends(get_db)):
    return db.query(models.AssembledPC).all()

@app.post("/pc/sell/{pc_id}")
def sell_pc(pc_id: int, final_price: float, db: Session = Depends(get_db)):
    pc = db.query(models.AssembledPC).filter(models.AssembledPC.id == pc_id).first()
    pc.sale_price = final_price
    pc.is_sold = True
    pc.profit = final_price - pc.total_cost
    db.commit()
    return {"profit": pc.profit}