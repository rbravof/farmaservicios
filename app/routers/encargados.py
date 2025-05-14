from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from fastapi import Form
from app.models import Encargado, Paciente
from app.schemas import EncargadoOut

router = APIRouter(
    prefix="/encargados",
    tags=["Encargados"]
)

@router.post("/crear")
def crear_encargado(
    rut_paciente: str = Form(...),
    rut_encargado: str = Form(...),
    nombre_encargado: str = Form(...),
    direccion: str = Form(""),
    comuna: str = Form(""),
    parentesco: str = Form(""),
    telefono: str = Form(""),
    correo: str = Form(""),
    db: Session = Depends(get_db)
):
    nuevo = models.Encargado(
        rut_paciente=rut_paciente,
        rut_encargado=rut_encargado,
        nombre=nombre_encargado,
        direccion=direccion,
        comuna=comuna,
        parentesco=parentesco,
        telefono=telefono,
        correo=correo
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Encargado registrado correctamente"}

@router.get("/por-paciente/{rut_paciente}", response_model=EncargadoOut)
def obtener_encargado_por_paciente(rut_paciente: str, db: Session = Depends(get_db)):
    encargado = db.query(models.Encargado).filter(models.Encargado.rut_paciente == rut_paciente).first()
    if not encargado:
        raise HTTPException(status_code=404, detail="Encargado no encontrado")
    return encargado


@router.delete("/eliminar/{rut_paciente}")
def eliminar_encargado_por_paciente(rut_paciente: str, db: Session = Depends(get_db)):
    encargado = db.query(Encargado).filter(Encargado.rut_paciente == rut_paciente).first()
    if not encargado:
        raise HTTPException(status_code=404, detail="Encargado no encontrado")
    db.delete(encargado)
    db.commit()
    return {"mensaje": "Encargado eliminado"}

@router.put("/editar/{rut_paciente}")
def editar_encargado(
    rut_paciente: str,
    rut_encargado: str = Form(...),
    nombre_encargado: str = Form(...),
    direccion: str = Form(""),
    comuna: str = Form(""),
    parentesco: str = Form(""),
    telefono: str = Form(""),
    correo: str = Form(""),
    db: Session = Depends(get_db)
):
    encargado = db.query(Encargado).filter(Encargado.rut_paciente == rut_paciente).first()
    if not encargado:
        raise HTTPException(status_code=404, detail="Encargado no encontrado")

    encargado.rut_encargado = rut_encargado
    encargado.nombre = nombre_encargado
    encargado.direccion = direccion
    encargado.comuna = comuna
    encargado.parentesco = parentesco
    encargado.telefono = telefono
    encargado.correo = correo

    db.commit()
    return {"mensaje": "Encargado actualizado correctamente"}
