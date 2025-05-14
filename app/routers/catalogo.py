from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from app.models import Producto
from app.schemas import ProductoCreate, ProductoResponse, ProductoUpdate, ProductoOut
from typing import List

router = APIRouter(
    prefix="/api/catalogo",
    tags=["Catálogo"]
)

# ========================
# CRUD BÁSICO DE PRODUCTOS
# ========================

@router.get("/", response_model=list[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    db_producto = Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.put("/{codigo}", response_model=ProductoResponse)
def actualizar_producto(codigo: str, datos: ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/{codigo}")
def eliminar_producto(codigo: str, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}


@router.get("/productos", response_model=list[ProductoResponse])
def obtener_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos

@router.get("/listar")
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos

@router.get("/buscar-principios")
def buscar_principios(q: str = "", db: Session = Depends(get_db)):
    resultados = (
        db.query(Producto.principio_activo)
        .filter(Producto.principio_activo.ilike(f"%{q}%"))
        .distinct()
        .limit(10)
        .all()
    )
    return [r[0] for r in resultados if r[0]]

@router.get("/buscar-laboratorios")
def buscar_laboratorios(q: str = "", db: Session = Depends(get_db)):
    resultados = (
        db.query(Producto.laboratorio)
        .filter(Producto.laboratorio.ilike(f"%{q}%"))
        .distinct()
        .limit(10)
        .all()
    )
    return [r[0] for r in resultados if r[0]]

@router.get("/productos/buscar")
def buscar_productos(nombre: str, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.nombre.ilike(f"%{nombre}%")).all()
    return productos

@router.get("/buscar")
def buscar_productos(nombre: str, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.nombre.ilike(f"%{nombre}%")).all()
    return productos

@router.get("/buscar-formatos")
def buscar_formatos(q: str = "", db: Session = Depends(get_db)):
    resultados = (
        db.query(Producto.formato)
        .filter(Producto.formato.ilike(f"%{q}%"))
        .distinct()
        .limit(10)
        .all()
    )
    return [r[0] for r in resultados if r[0]]

# ✅ Este es el endpoint correcto que debes dejar para buscar por nombre
@router.get("/buscar-productos/{nombre}", response_model=List[schemas.ProductoOut])
def buscar_productos_por_nombre(nombre: str, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.nombre.ilike(f"%{nombre}%")).limit(10).all()
    return productos

# ============================
# CARGA MASIVA DESDE JSON
# ============================

@router.post("/carga-masiva")
async def guardar_productos(productos: list[ProductoCreate], db: Session = Depends(get_db)):
    try:
        print(f"🔄 Recibidos {len(productos)} productos")
        productos_insertados = 0

        for producto in productos:
            codigo_str = str(producto.codigo)
            print(f"🔍 Verificando código: {codigo_str}")

            existe = db.query(Producto).filter(Producto.codigo == codigo_str).first()

            if not existe:
                nuevo = Producto(
                    codigo=codigo_str,
                    nombre=producto.nombre,
                    principio_activo=producto.principio_activo,
                    laboratorio=producto.laboratorio,
                    formato=producto.formato,
                    precio_compra_neto=producto.precio_compra_neto,
                    precio_venta_neto=producto.precio_venta_neto,
                    precio_venta=producto.precio_venta
                )
                db.add(nuevo)
                productos_insertados += 1
                print(f"✅ Insertado: {codigo_str}")
            else:
                print(f"⚠️ Ya existe: {codigo_str}")

        db.commit()
        print(f"✅ {productos_insertados} productos insertados")
        return {"mensaje": f"✅ {productos_insertados} productos cargados correctamente"}

    except Exception as e:
        print("🚨 Error general en carga masiva:")
        print(e)
        raise HTTPException(status_code=500, detail="Error en la carga")

@router.get("/producto-por-codigo/{codigo}", response_model=schemas.ProductoOut)
def obtener_producto_por_codigo(codigo: str, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
