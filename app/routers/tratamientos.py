from fastapi import APIRouter, Form, Depends, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from sqlalchemy import and_, func
from uuid import uuid4
from datetime import date, timedelta
import smtplib
import os

from app import models, schemas
from app.models import Tratamiento, Paciente, Encargado, Contacto
from app.schemas import TratamientoBase, TratamientoResponse
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/tratamientos", tags=["Tratamientos"])
#router = APIRouter(prefix="/contactos", tags=["Contactos"])

templates = Jinja2Templates(directory="app/templates")

# Variables de entorno seguras
correo_origen = os.getenv("CORREO_ORIGEN")
clave_origen = os.getenv("CLAVE_CORREO")

# -------------------------------
# Guardar tratamiento
# -------------------------------
@router.post("/guardar")
def guardar_tratamiento(
    rut_paciente: str = Form(...),
    nombre_medicamento: str = Form(...),
    codigo_barra: str = Form(None),
    cantidad_por_caja: int = Form(...),
    dosis_diaria: int = Form(...),
    duracion_dias: int = Form(...),
    fecha_fin: date = Form(...),
    db: Session = Depends(get_db)
):
    tratamiento = Tratamiento(
        rut_paciente=rut_paciente,
        nombre_medicamento=nombre_medicamento,
        codigo_barra=codigo_barra,
        cantidad_por_caja=cantidad_por_caja,
        dosis_diaria=dosis_diaria,
        duracion_dias=duracion_dias,
        fecha_fin=fecha_fin
    )
    db.add(tratamiento)
    db.commit()
    return {"mensaje": "Tratamiento guardado correctamente"}

@router.put("/editar/{id}")
def editar_tratamiento(
    id: int,
    rut_paciente: str = Form(...),
    nombre_medicamento: str = Form(...),
    codigo_barra: str = Form(None),
    cantidad_por_caja: int = Form(...),
    dosis_diaria: int = Form(...),
    duracion_dias: int = Form(...),
    fecha_fin: date = Form(...),
    db: Session = Depends(get_db)
):
    tratamiento = db.query(Tratamiento).filter(Tratamiento.id == id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    tratamiento.rut_paciente = rut_paciente
    tratamiento.nombre_medicamento = nombre_medicamento
    tratamiento.codigo_barra = codigo_barra
    tratamiento.cantidad_por_caja = cantidad_por_caja
    tratamiento.dosis_diaria = dosis_diaria
    tratamiento.duracion_dias = duracion_dias
    tratamiento.fecha_fin = fecha_fin

    db.commit()
    return {"mensaje": "Tratamiento actualizado correctamente"}

@router.get("/recetas/{rut_paciente}")
def listar_recetas_paciente(rut_paciente: str):
    carpeta = "app/static/recetas"
    if not os.path.exists(carpeta):
        return []
    return [
        {
            "nombre": archivo,
            "url": f"/static/recetas/{archivo}"
        }
        for archivo in os.listdir(carpeta)
        if archivo.startswith(rut_paciente)
    ]

@router.delete("/eliminar-receta/{nombre_archivo}")
def eliminar_receta(nombre_archivo: str):
    ruta = os.path.join("app/static/recetas", nombre_archivo)
    if os.path.exists(ruta):
        os.remove(ruta)
        return {"mensaje": "Receta eliminada"}
    raise HTTPException(status_code=404, detail="Archivo no encontrado")

@router.delete("/eliminar/{id}")
def eliminar_tratamiento(id: int, db: Session = Depends(get_db)):
    tratamiento = db.query(Tratamiento).filter(Tratamiento.id == id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    db.delete(tratamiento)
    db.commit()
    return {"mensaje": "Tratamiento eliminado correctamente"}


# -------------------------------
# Verificar si existe tratamiento
# -------------------------------
@router.get("/existe/{rut_paciente}")
def tratamiento_existe(rut_paciente: str, db: Session = Depends(get_db)):
    existe = db.query(Tratamiento).filter(Tratamiento.rut_paciente == rut_paciente).first()
    return {"existe": existe is not None}

# -------------------------------
# Obtener tratamientos por paciente (oficial)
# -------------------------------
@router.get("/por-paciente/{rut_paciente}")
def obtener_tratamientos_paciente(rut_paciente: str, db: Session = Depends(get_db)):
    resultados = (
        db.query(
            Tratamiento.id,
            Tratamiento.rut_paciente,
            Tratamiento.nombre_medicamento,
            Tratamiento.codigo_barra,
            Tratamiento.cantidad_por_caja,
            Tratamiento.dosis_diaria,
            Tratamiento.duracion_dias,
            Tratamiento.fecha_fin,
            models.Producto.principio_activo,
            models.Producto.laboratorio,
            models.Producto.precio_venta,
        )
        .outerjoin(models.Producto, Tratamiento.codigo_barra == models.Producto.codigo)
        .filter(Tratamiento.rut_paciente == rut_paciente)
        .all()
    )

    return [dict(r._asdict()) for r in resultados]


# -------------------------------
# Vista HTML
# -------------------------------
@router.get("/tratamiento", response_class=HTMLResponse)
def tratamiento_form(request: Request, rut: str):
    return templates.TemplateResponse("tratamiento_paciente.html", {"request": request, "rut": rut})

@router.get("/ver-tratamiento", response_class=HTMLResponse)
def ver_tratamiento_html(request: Request):
    return templates.TemplateResponse("ver_tratamiento.html", {"request": request})

# -------------------------------
# Tratamientos vencidos
# -------------------------------
@router.get("/vencidos")
def tratamientos_vencidos(db: Session = Depends(get_db)):
    hoy = date.today()
    limite = hoy + timedelta(days=5)

    tratamientos = (
        db.query(
            Tratamiento.id.label("id"),
            Paciente.rut.label("rut"),
            Paciente.nombre,
            Paciente.telefono,
            Paciente.correo,
            Tratamiento.nombre_medicamento,
            Tratamiento.fecha_fin
        )
        .join(Tratamiento, Tratamiento.rut_paciente == Paciente.rut)
        .filter(Tratamiento.fecha_fin > hoy)
        .filter(Tratamiento.fecha_fin <= limite)
        .all()
    )

    return [dict(t._asdict()) for t in tratamientos]

@router.post("/registrar-contacto")
def registrar_contacto(
    tipo_contacto: str = Form(...),
    rut_paciente: str = Form(...),
    nombre_medicamento: str = Form(...),
    usuario: str = Form(...),
    db: Session = Depends(get_db)
):
    hoy = datetime.utcnow().date()

    # Validar si ya se contactó hoy por el mismo tipo
    contacto_existente = db.query(Contacto).filter(
        Contacto.rut_paciente == rut_paciente,
        Contacto.tipo_contacto == tipo_contacto,
        Contacto.fecha_contacto >= hoy,
        Contacto.fecha_contacto < hoy + timedelta(days=1)
    ).first()

    if contacto_existente:
        raise HTTPException(status_code=400, detail=f"Este paciente ya fue contactado hoy por {tipo_contacto}.")

    nuevo_contacto = Contacto(
        rut_paciente=rut_paciente,
        nombre_medicamento=nombre_medicamento,
        tipo_contacto=tipo_contacto,
        usuario=usuario
    )
    db.add(nuevo_contacto)
    db.commit()
    return {"mensaje": "Contacto registrado exitosamente"}

# -------------------------------
# Tratamientos próximos a vencer
# -------------------------------
@router.get("/vencimientos")
def obtener_tratamientos_proximos_a_vencer(db: Session = Depends(get_db)):
    hoy = date.today()
    resultados = (
        db.query(
            Tratamiento.rut_paciente,
            Tratamiento.nombre_medicamento,
            Tratamiento.fecha_fin,
            Paciente.nombre.label("nombre_paciente"),
            Paciente.correo,
            Paciente.telefono
        )
        .join(Paciente, Tratamiento.rut_paciente == Paciente.rut)
        .filter(Tratamiento.fecha_fin >= hoy)
        .all()
    )
    return [
        {
            "rut_paciente": r.rut_paciente,
            "nombre_medicamento": r.nombre_medicamento,
            "fecha_fin": r.fecha_fin,
            "nombre_paciente": r.nombre_paciente,
            "correo": r.correo,
            "telefono": r.telefono,
        }
        for r in resultados
    ]

@router.get("/por-vencer")
def obtener_tratamientos_por_vencer(db: Session = Depends(get_db)):
    hoy = date.today()
    limite = hoy + timedelta(days=5)

    tratamientos = db.query(models.Tratamiento).join(models.Paciente).filter(
        models.Tratamiento.fecha_fin >= hoy,
        models.Tratamiento.fecha_fin <= limite
    ).all()

    resultado = []
    for t in tratamientos:
        resultado.append({
            "rut_paciente": t.rut_paciente,
            "nombre_paciente": t.paciente.nombre,
            "nombre_medicamento": t.nombre_medicamento,
            "fecha_fin": t.fecha_fin.isoformat(),
            "telefono": t.paciente.telefono,
            "correo": t.paciente.correo,
            "direccion": t.paciente.direccion,
            "comuna": t.paciente.comuna
        })

    return resultado

# -------------------------------
# Enviar correo
# -------------------------------
@router.post("/enviar-correo")
async def enviar_correo_backend(
    request: Request,
    correo: str = Form(...),
    nombre: str = Form(...),
    medicamento: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        contenido_html = templates.get_template("correos/aviso_vencimiento.html").render({
            "nombre": nombre,
            "medicamento": medicamento
        })

        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = "Recordatorio de Medicamento por Vencer"
        mensaje["From"] = correo_origen
        mensaje["To"] = correo
        parte_html = MIMEText(contenido_html, "html")
        mensaje.attach(parte_html)

        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(correo_origen, clave_origen)
            servidor.sendmail(mensaje["From"], mensaje["To"], mensaje.as_string())

        return JSONResponse(content={"mensaje": "✅ Correo enviado correctamente."})
    except Exception as e:
        print("❌ Error al enviar correo:", e)
        return JSONResponse(status_code=500, content={"error": "Error al enviar correo."})

# -------------------------------
# Subida de receta
# -------------------------------
@router.post("/subir-receta")
async def subir_receta(
    rut_paciente: str = Form(...),
    nombre_paciente: str = Form(...),
    file: UploadFile = File(...)
):
    carpeta = "app/static/recetas"
    os.makedirs(carpeta, exist_ok=True)

    # Limpiar nombre
    nombre_limpio = nombre_paciente.replace(" ", "_")
    base_nombre = f"{rut_paciente}_{nombre_limpio}_Receta"

    # Buscar correlativo
    existentes = [
        f for f in os.listdir(carpeta)
        if f.startswith(f"{rut_paciente}_{nombre_limpio}_Receta")
    ]
    correlativo = len(existentes) + 1

    extension = os.path.splitext(file.filename)[1]
    nombre_final = f"{base_nombre}_{correlativo}{extension}"
    ruta_archivo = os.path.join(carpeta, nombre_final)

    with open(ruta_archivo, "wb") as f:
        contenido = await file.read()
        f.write(contenido)

    return {"mensaje": "Receta subida con éxito", "archivo": nombre_final}
 

# -------------------------------
# Búsqueda de pacientes y productos
# -------------------------------
@router.get("/buscar-pacientes")
def buscar_pacientes_por_nombre(nombre: str, db: Session = Depends(get_db)):
    resultados = db.query(Paciente).filter(Paciente.nombre.ilike(f"%{nombre}%")).limit(10).all()
    return [{"rut": p.rut, "nombre": p.nombre} for p in resultados]

@router.get("/buscar-productos/{nombre}")
def buscar_productos(nombre: str, db: Session = Depends(get_db)):
    if len(nombre) < 3:
        return []
    productos = db.query(models.Producto).filter(models.Producto.nombre.ilike(f"%{nombre}%")).limit(10).all()
    return productos

@router.get("/tratamientos-vencidos", response_class=HTMLResponse)
def mostrar_tratamientos_vencidos(request: Request):
    return templates.TemplateResponse("tratamientos_vencidos.html", {"request": request})

@router.get("/historial-contactos")
def historial_contactos(db: Session = Depends(get_db)):
    contactos = (
        db.query(
            Contacto.rut_paciente,
            Contacto.nombre_medicamento,
            Contacto.tipo_contacto,
            Contacto.fecha_contacto,
            Contacto.usuario,
            models.Usuario.telefono.label("telefono_usuario")
        )
        .join(models.Usuario, func.lower(Contacto.usuario) == func.lower(models.Usuario.usuario))
        .order_by(Contacto.fecha_contacto.desc())
        .all()
    )

    return [
        {
            "rut_paciente": c.rut_paciente,
            "nombre_medicamento": c.nombre_medicamento,
            "tipo_contacto": c.tipo_contacto,
            "fecha_contacto": c.fecha_contacto,
            "usuario": c.usuario,
            "telefono_usuario": c.telefono_usuario
        }
        for c in contactos
    ]


@router.get("/contactos/pendientes")
def obtener_contactos_pendientes(usuario: str, db: Session = Depends(get_db)):
    hoy = date.today()
    limite = hoy + timedelta(days=5)

    tratamientos = db.query(models.Tratamiento).join(models.Paciente).filter(
        models.Tratamiento.fecha_fin >= hoy,
        models.Tratamiento.fecha_fin <= limite
    ).all()

    resultados = []

    for t in tratamientos:
        contacto = db.query(models.Contacto).filter(
            models.Contacto.rut_paciente == t.rut_paciente,
            models.Contacto.fecha == hoy,
            models.Contacto.usuario == usuario
        ).first()

        resultados.append({
            "rut_paciente": t.rut_paciente,
            "nombre": t.paciente.nombre,
            "medicamento": t.nombre_medicamento,
            "fecha_fin": t.fecha_fin,
            "contactado_hoy": bool(contacto),
            "medio_contacto": contacto.medio if contacto else None
        })

    return resultados
    
def actualizar_tratamientos_vencidos(db: Session = Depends(get_db)):
    hoy = date.today()
    tratamientos = db.query(models.Tratamiento).filter(
        models.Tratamiento.fecha_fin < hoy,
        models.Tratamiento.estado == "Activo"
    ).all()

    for t in tratamientos:
        historico = models.HistTratamiento(
            rut_paciente=t.rut_paciente,
            nombre_medicamento=t.nombre_medicamento,
            fecha_inicio=t.fecha_inicio,
            fecha_fin=t.fecha_fin,
            estado="No Compra",  # 👈 O lógica condicional si corresponde
            fecha_historico=datetime.now()
        )
        db.add(historico)
        db.delete(t)

    db.commit()
    
@router.post("/comprar/{id_tratamiento}")
def comprar_tratamiento(id_tratamiento: int, db: Session = Depends(get_db)):
    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id == id_tratamiento).first()

    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    hoy = date.today()

    if tratamiento.fecha_fin <= hoy:
        raise HTTPException(status_code=400, detail="El tratamiento ya está vencido")

    dias_restantes = (tratamiento.fecha_fin - hoy).days
    comprimidos_restantes = max((dias_restantes - 1) * tratamiento.dosis_diaria, 0) if dias_restantes > 0 else 0
    comprimidos_nuevos = tratamiento.cantidad_por_caja
    total_comprimidos = comprimidos_restantes + comprimidos_nuevos

    if tratamiento.dosis_diaria == 0:
        raise HTTPException(status_code=400, detail="Dosis diaria inválida")

    nueva_duracion_dias = total_comprimidos // tratamiento.dosis_diaria
    fecha_fin = hoy + timedelta(days=nueva_duracion_dias)

    nuevo_tratamiento = models.Tratamiento(
        rut_paciente=tratamiento.rut_paciente,
        codigo_barra=tratamiento.codigo_barra,
        nombre_medicamento=tratamiento.nombre_medicamento,
        dosis_diaria=tratamiento.dosis_diaria,
        cantidad_por_caja=tratamiento.cantidad_por_caja,
        fecha_fin=fecha_fin
    )

    historico = models.HistTratamiento(
        rut_paciente=tratamiento.rut_paciente,
        codigo_barra=tratamiento.codigo_barra,
        nombre_medicamento=tratamiento.nombre_medicamento,
        dosis_diaria=tratamiento.dosis_diaria,
        cantidad_por_caja=tratamiento.cantidad_por_caja,
        fecha_inicio=tratamiento.fecha_inicio,  # 👈 esta línea es clave
        fecha_fin=tratamiento.fecha_fin,
        estado="Comprado",
        fecha_fin_real=hoy
    )


    try:
        db.add(nuevo_tratamiento)
        db.flush()
        db.refresh(nuevo_tratamiento)

        db.add(historico)
        db.delete(tratamiento)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la transacción: {str(e)}")

    return {"mensaje": "Tratamiento renovado correctamente", "nuevo_id": nuevo_tratamiento.id}
