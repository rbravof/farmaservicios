from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Sucursal, Farmacia, SucEncargado, Usuario
from app.schemas import SucursalEncargadoSchema


router = APIRouter()

# Crear sucursal + encargado
@router.post("/crear")
def crear_sucursal(data: SucursalEncargadoSchema, db: Session = Depends(get_db)):
    nueva_sucursal = Sucursal(
        id_farmacia=data.id_farmacia,
        nombre=data.nombre,
        direccion=data.direccion,
        comuna=data.comuna,
        region=data.region,
        telefono=data.telefono,
        correo_sucursal=data.correo_sucursal
    )
    db.add(nueva_sucursal)
    db.commit()
    db.refresh(nueva_sucursal)

    if data.rut_encargado and data.nombre_encargado:
        nuevo_encargado = SucEncargado(
            id_sucursal=nueva_sucursal.id_sucursal,
            rut_encargado=data.rut_encargado,
            nombre_encargado=data.nombre_encargado,
            telefono_encargado=data.telefono_encargado,
            correo_encargado=data.correo_encargado
        )
        db.add(nuevo_encargado)
        db.commit()

    return {"mensaje": "Sucursal creada correctamente"}


# Listar sucursales + encargados
@router.get("/listar")
def listar_sucursales(db: Session = Depends(get_db)):
    sucursales = db.query(Sucursal).all()
    resultado = []

    for sucursal in sucursales:
        farmacia = db.query(Farmacia).filter(Farmacia.id == sucursal.id_farmacia).first()
        encargado = db.query(SucEncargado).filter(SucEncargado.id_sucursal == sucursal.id_sucursal).first()

        resultado.append({
            "id": sucursal.id_sucursal,
            "nombre": sucursal.nombre,
            "direccion": sucursal.direccion,
            "region": sucursal.region,
            "comuna": sucursal.comuna,
            "telefono": sucursal.telefono,
            "farmacia": farmacia.razon_social if farmacia else "No asociada",
            "encargado_rut": encargado.rut_encargado if encargado else "",
            "encargado_nombre": encargado.nombre_encargado if encargado else "",
            "encargado_telefono": encargado.telefono_encargado if encargado else "",
            "encargado_correo": encargado.correo_encargado if encargado else ""
        })

    return resultado

# Editar sucursal + encargado
@router.put("/editar/{id_sucursal}")
def editar_sucursal(
    id_sucursal: int,
    data: SucursalEncargadoSchema,
    db: Session = Depends(get_db)
):
    sucursal = db.query(Sucursal).filter(Sucursal.id_sucursal == id_sucursal).first()

    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    sucursal.nombre = data.nombre
    sucursal.direccion = data.direccion
    sucursal.region = data.region
    sucursal.comuna = data.comuna
    sucursal.telefono = data.telefono
    sucursal.correo_sucursal = data.correo_sucursal
    sucursal.id_farmacia = data.id_farmacia
    db.commit()

    encargado = db.query(SucEncargado).filter(SucEncargado.id_sucursal == id_sucursal).first()

    if encargado:
        encargado.rut_encargado = data.rut_encargado
        encargado.nombre_encargado = data.nombre_encargado
        encargado.telefono_encargado = data.telefono_encargado
        encargado.correo_encargado = data.correo_encargado
    else:
        nuevo_encargado = SucEncargado(
            rut_encargado=data.rut_encargado,
            nombre_encargado=data.nombre_encargado,
            telefono_encargado=data.telefono_encargado,
            correo_encargado=data.correo_encargado,
            id_sucursal=id_sucursal
        )
        db.add(nuevo_encargado)

    db.commit()

    return {"message": "Sucursal y encargado actualizados exitosamente"}

# Eliminar sucursal con validación de usuarios asociados
@router.delete("/eliminar/{id}")
def eliminar_sucursal(id: int, db: Session = Depends(get_db)):
    # Verificar si existen usuarios asociados a esta sucursal
    usuarios = db.query(Usuario).filter(Usuario.id_sucursal == id).first()
    if usuarios:
        raise HTTPException(status_code=400, detail="No se puede eliminar la sucursal, ya que tiene usuarios asociados.")

    sucursal = db.query(Sucursal).filter(Sucursal.id == id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    db.delete(sucursal)
    db.commit()
    return {"mensaje": "Sucursal eliminada exitosamente"}


@router.get("/obtener/{id_sucursal}")
def obtener_sucursal(id_sucursal: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id_sucursal == id_sucursal).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    encargado = db.query(SucEncargado).filter(SucEncargado.id_sucursal == id_sucursal).first()

    return {
        "id": sucursal.id_sucursal,
        "id_farmacia": sucursal.id_farmacia,
        "nombre": sucursal.nombre,
        "direccion": sucursal.direccion,
        "region": sucursal.region,
        "comuna": sucursal.comuna,
        "telefono": sucursal.telefono,
        "correo_sucursal": sucursal.correo_sucursal,
        "encargado_rut": encargado.rut_encargado if encargado else "",
        "encargado_nombre": encargado.nombre_encargado if encargado else "",
        "encargado_telefono": encargado.telefono_encargado if encargado else "",
        "encargado_correo": encargado.correo_encargado if encargado else ""
    }

@router.get("/por-farmacia/{id_farmacia}")
def obtener_sucursales_por_farmacia(id_farmacia: int, db: Session = Depends(get_db)):
    sucursales = db.query(Sucursal).filter(Sucursal.id_farmacia == id_farmacia).all()
    
    resultado = []
    for sucursal in sucursales:
        resultado.append({
            "id": sucursal.id_sucursal,
            "nombre": sucursal.nombre
        })
    
    return resultado

@router.get("/obtener/{id}")
def obtener_sucursal(id: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id_sucursal == id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    return {
        "id": sucursal.id_sucursal,
        "id_farmacia": sucursal.id_farmacia,
        "nombre": sucursal.nombre,
        "direccion": sucursal.direccion,
        "comuna": sucursal.comuna,
        "region": sucursal.region,
        "telefono": sucursal.telefono,
        "correo_sucursal": sucursal.correo_sucursal,
        "rut_encargado": sucursal.rut_encargado,
        "nombre_encargado": sucursal.nombre_encargado,
        "telefono_encargado": sucursal.telefono_encargado,
        "correo_encargado": sucursal.correo_encargado
    }
