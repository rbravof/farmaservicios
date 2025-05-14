from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# ✅ Esto funciona con uvicorn main:app
from app import models, schemas
from app.database import get_db
from app.models import Farmacia
from typing import List





#router = APIRouter(prefix="/admin", tags=["Administración"])
router = APIRouter(tags=["Administración"])


# --- Sucursales ---
@router.post("/sucursales/", response_model=schemas.SucursalResponse)
def crear_sucursal(sucursal: schemas.SucursalCreate, db: Session = Depends(get_db)):
    nueva = models.Sucursal(**sucursal.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/sucursales/", response_model=list[schemas.SucursalResponse])
def listar_sucursales(db: Session = Depends(get_db)):
    return db.query(models.Sucursal).all()

# --- Usuarios ---
@router.post("/usuarios/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    nuevo = models.Usuario(**usuario.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/usuarios/", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

# --- Farmacias ---
@router.get("/farmacias/", response_model=List[schemas.FarmaciaConEncargadoResponse])
def listar_farmacias(db: Session = Depends(get_db)):
    farmacias = db.query(Farmacia).all()
    return [
        {
            "id": f.id,
            "rut": f.rut,
            "razon_social": f.razon_social,
            "direccion": f.direccion,
            "region": f.region,
            "comuna": f.comuna,
            "telefono": f.telefono,
            "correo": f.correo,
            "encargado_rut": f.encargado_rut,
            "encargado_nombre": f.encargado_nombre,
            "encargado_telefono": f.encargado_telefono,
            "encargado_correo": f.encargado_correo,
        }
        for f in farmacias
    ]



@router.get("/farmacias/listar", response_model=list[schemas.FarmaciaResponse])
def listar_farmacias(db: Session = Depends(get_db)):
    return db.query(models.Farmacia).all()

@router.delete("/farmacias/{farmacia_id}")
def eliminar_farmacia(farmacia_id: int, db: Session = Depends(get_db)):
    farmacia = db.query(models.Farmacia).get(farmacia_id)
    if not farmacia:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")
    db.delete(farmacia)
    db.commit()
    return {"mensaje": "Eliminada correctamente"}

@router.put("/farmacias/{farmacia_id}", response_model=schemas.FarmaciaResponse)
def actualizar_farmacia(farmacia_id: int, datos: schemas.FarmaciaCreate, db: Session = Depends(get_db)):
    farmacia = db.query(models.Farmacia).get(farmacia_id)
    if not farmacia:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")
    
    for campo, valor in datos.dict().items():
        setattr(farmacia, campo, valor)

    db.commit()
    db.refresh(farmacia)
    return farmacia
