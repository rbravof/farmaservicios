# app/routers/pacientes.py
from fastapi import Path, APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas
from app.models import Tratamiento, Paciente, Encargado
import traceback

router = APIRouter()

@router.get("/pacientes/obtener/{rut}")
def obtener_paciente(rut: str, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente

from sqlalchemy.exc import IntegrityError

@router.post("/crear")
def crear_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = models.Paciente(**paciente.dict())
    db.add(db_paciente)
    try:
        db.commit()
        db.refresh(db_paciente)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe un paciente con este RUT.")
    
    return {"mensaje": "Paciente creado exitosamente", "paciente": db_paciente}


@router.get("/listar-con-encargado")
def listar_pacientes_con_encargado(db: Session = Depends(get_db)):
    pacientes = db.query(models.Paciente).all()
    resultados = []
    for p in pacientes:
        tiene_encargado = db.query(models.Encargado).filter(models.Encargado.rut_paciente == p.rut).first() is not None
        tiene_tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.rut_paciente == p.rut).first() is not None

        # 🔥 imprimimos para ver si realmente se carga
        print(f"{p.rut} → fecha_creacion: {getattr(p, 'fecha_creacion', 'NO EXISTE')}")

        resultados.append({
            "rut": p.rut,
            "nombre": p.nombre,
            "edad": p.edad,
            "comuna": p.comuna,
            "telefono": p.telefono,
            "correo": p.correo,
            "fecha_creacion": p.fecha_creacion.isoformat() if p.fecha_creacion else None,
            "encargado": tiene_encargado,
            "tiene_tratamiento": tiene_tratamiento
        })
    return resultados





@router.get("/tratamiento/ver/{rut_paciente}")
def verificar_tratamiento(rut_paciente: str, db: Session = Depends(get_db)):
    tratamientos = db.query(Tratamiento).filter_by(rut_paciente=rut_paciente).all()
    if tratamientos:
        return RedirectResponse(url=f"/ver-tratamiento?rut={rut_paciente}")
    else:
        return RedirectResponse(url="/tratamiento-paciente")

@router.get("/detalle/{rut}")
def obtener_detalle_paciente(
    rut: str = Path(...),
    db: Session = Depends(get_db)
):
    try:
        paciente = db.query(models.Paciente).options(joinedload(models.Paciente.encargado)).filter(models.Paciente.rut == rut).first()
        
        if not paciente:
            return JSONResponse(status_code=404, content={"error": "Paciente no encontrado"})

        datos = {
            "nombre": paciente.nombre,
            "edad": paciente.edad,
            "direccion": paciente.direccion,
            "comuna": paciente.comuna,
            "correo": paciente.correo,
            "telefono": paciente.telefono,
            "encargado": None
        }

        if paciente.encargado:
            datos["encargado"] = {
                "nombre": paciente.encargado.nombre,
                "correo": paciente.encargado.correo,
                "telefono": paciente.encargado.telefono,
            }

        return datos

    except Exception as e:
        print("❌ ERROR EN DETALLE PACIENTE:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "Error interno del servidor"})

@router.get("/")
def listar_pacientes(db: Session = Depends(get_db)):
    pacientes = db.query(Paciente).all()
    return pacientes
    
@router.get("/por-rut/{rut}")
def obtener_paciente_por_rut(
    rut: str = Path(...),
    db: Session = Depends(get_db)
):
    paciente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {
        "rut": paciente.rut,
        "nombre": paciente.nombre,
        "fecha_nacimiento": str(paciente.fecha_nacimiento),
        "edad": paciente.edad,
        "direccion": paciente.direccion,
        "comuna": paciente.comuna,
        "region": paciente.region,
        "telefono": paciente.telefono,
        "correo": paciente.correo,
    }

@router.put("/editar/{rut}")
def editar_paciente(rut: str, paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Actualizar todos los campos
    for campo, valor in paciente.dict().items():
        setattr(db_paciente, campo, valor)

    db.commit()
    db.refresh(db_paciente)
    return {"mensaje": "Paciente actualizado exitosamente", "paciente": db_paciente}

@router.delete("/eliminar/{rut}")
def eliminar_paciente(rut: str, db: Session = Depends(get_db)):
    # Buscar paciente
    paciente = db.query(Paciente).filter(Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Eliminar tratamientos asociados
    db.query(Tratamiento).filter(Tratamiento.rut_paciente == rut).delete()

    # Eliminar encargado asociado (si existe)
    db.query(Encargado).filter(Encargado.rut_paciente == rut).delete()

    # Eliminar paciente
    db.delete(paciente)
    db.commit()

    return {"mensaje": "Paciente, tratamientos y encargado eliminados correctamente"}
