# Archivo: app/routers/farmacias.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farmacia, Sucursal
from app import models, schemas

router = APIRouter()

@router.get("/farmacias/listar")
def listar_farmacias(db: Session = Depends(get_db)):
    farmacias = db.query(Farmacia).all()
    return [
        {
            "id": f.id,
            "rut": f.rut,
            "razon_social": f.razon_social,
            "comuna": f.comuna,
            "telefono": f.telefono,
            "correo": f.correo
        }
        for f in farmacias
    ]


@router.get("/farmacias/{id}", response_model=schemas.FarmaciaResponse)
def obtener_farmacia(id: int, db: Session = Depends(get_db)):
    farmacia = db.query(Farmacia).filter(Farmacia.id == id).first()
    if not farmacia:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")
    return farmacia

@router.get("/administracion/farmacias/")
def listar_farmacias_completo(db: Session = Depends(get_db)):
    farmacias = db.query(Farmacia).all()
    return [
        {
            "id": f.id,
            "rut": f.rut,
            "razon_social": f.razon_social,
            "comuna": f.comuna,
            "telefono": f.telefono,
            "correo": f.correo
        }
        for f in farmacias
    ]

@router.post("/administracion/farmacias/", response_model=schemas.FarmaciaResponse)
def crear_farmacia(farmacia: schemas.FarmaciaBase, db: Session = Depends(get_db)):
    nueva = models.Farmacia(**farmacia.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/administracion/farmacias/{id}", response_model=schemas.FarmaciaResponse)
def actualizar_farmacia(id: int, farmacia: schemas.FarmaciaBase, db: Session = Depends(get_db)):
    db_farmacia = db.query(Farmacia).filter(Farmacia.id == id).first()
    if not db_farmacia:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")

    for campo, valor in farmacia.dict().items():
        setattr(db_farmacia, campo, valor)

    db.commit()
    db.refresh(db_farmacia)
    return db_farmacia
    
@router.delete("/administracion/farmacias/{id}")
def eliminar_farmacia(id: int, db: Session = Depends(get_db)):
    farmacia = db.query(Farmacia).filter(Farmacia.id == id).first()
    if not farmacia:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")

    db.delete(farmacia)
    db.commit()
    return {"mensaje": "Farmacia eliminada correctamente"}

@router.delete("/eliminar/{id}")
def eliminar_farmacia(id: int, db: Session = Depends(get_db)):
    sucursales = db.query(Sucursal).filter(Sucursal.id_farmacia == id).first()
    if sucursales:
        raise HTTPException(status_code=400, detail="No se puede eliminar la farmacia, ya que tiene sucursales asociadas.")
    
    farmacia = db.query(Farmacia).filter(Farmacia.id == id).first()
    if not farmacia:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")
    
    db.delete(farmacia)
    db.commit()
    return {"mensaje": "Farmacia eliminada exitosamente"}
