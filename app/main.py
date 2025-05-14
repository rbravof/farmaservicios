from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from datetime import datetime
from app.routers import farmacias, usuarios
import os
import shutil
import psycopg2

# Importaciones locales
from app.database import Base, get_db
from app.models import Paciente, Tratamiento, Usuario, Farmacia, Sucursal
from app.schemas import PacienteCreate, PacienteResponse, TratamientoCreate, UsuarioLogin
from app.utils.security import verificar_contraseña
import app.routers.reporte_vencimientos_diario

# Routers
from app.routers import (
    reporte_vencimientos_diario,
    test_envio_router,
    usuarios,
    administracion,
    catalogo,
    pacientes,
    encargados,
    tratamientos,# <- ¡ya estaba bien importado aquí!
    sucursales  
)

# -----------------------
# Configuración Inicial
# -----------------------

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estáticos y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="app/templates")

# -----------------------
# Rutas API
# -----------------------

# Routers API
# Routers API

app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(administracion.router, prefix="/api/administracion")
app.include_router(catalogo.router)
app.include_router(pacientes.router, prefix="/api/pacientes")
app.include_router(encargados.router, prefix="/api")
app.include_router(tratamientos.router)
app.include_router(test_envio_router.router, prefix="/api/test")
app.include_router(sucursales.router, prefix="/api/sucursales")
app.include_router(farmacias.router, prefix="/api") 

# -----------------------
# Endpoints específicos HTML
# -----------------------


@app.get("/registro_contacto", response_class=HTMLResponse)
async def formulario_registro_contacto(request: Request):
    return templates.TemplateResponse("registro_contacto.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
def root_redirect(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(usuario_login: UsuarioLogin, db: Session = Depends(get_db)):
    username = usuario_login.usuario
    password = usuario_login.contrasena

    # Buscar el usuario
    usuario = db.query(Usuario).filter(Usuario.usuario == username).first()

    if not usuario or usuario.contrasena != password:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    # 🔥 Corrección: buscar sucursal y luego farmacia
    sucursal = db.query(Sucursal).filter(Sucursal.id_sucursal == usuario.id_sucursal).first()
    farmacia = db.query(Farmacia).filter(Farmacia.id == sucursal.id_farmacia).first()

    nombre_farmacia = farmacia.razon_social if farmacia else "Sin Farmacia"

    # Devolver datos útiles
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "id_farmacia": sucursal.id_farmacia,
        "nombre_farmacia": nombre_farmacia
    }


def mover_tratamientos_a_historial():
    db: Session = SessionLocal()
    try:
        # 1. Obtener tratamientos vencidos sin estado o con estado vacío
        tratamientos_vencidos = db.query(Tratamiento).filter(
            Tratamiento.fecha_fin < datetime.today(),
            (Tratamiento.estado == None) | (Tratamiento.estado == "")
        ).all()

        for t in tratamientos_vencidos:
            # 2. Crear entrada en historial
            hist = HistTratamiento(
                id_tratamiento=t.id,
                rut_paciente=t.rut_paciente,
                nombre_medicamento=t.nombre_medicamento,
                fecha_inicio=t.fecha_inicio,
                fecha_fin=t.fecha_fin,
                dosis=t.dosis,
                estado="No Compra",
                fecha_movimiento=datetime.now()
            )
            db.add(hist)

            # 3. Marcar tratamiento original como "No Compra"
            t.estado = "No Compra"

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Error al mover tratamientos a historial: {e}")
    finally:
        db.close()

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(mover_tratamientos_a_historial, 'cron', hour=7, minute=0)
scheduler.start()
print("🕖 Cron job activado: mueve tratamientos vencidos a las 07:00 AM.")

@app.get("/formulario_usuario", response_class=HTMLResponse)
async def formulario_usuario(request: Request):
    return templates.TemplateResponse("formulario_usuario.html", {"request": request})


# HTML templates
@app.get("/dashboard", response_class=HTMLResponse)
def mostrar_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
    
@app.get("/tratamientos-vencidos", response_class=HTMLResponse)
def mostrar_tratamientos_vencidos(request: Request):
    return templates.TemplateResponse("tratamientos_vencidos.html", {"request": request})


@app.get("/registro-pacientes", response_class=HTMLResponse)
def mostrar_formulario_pacientes(request: Request):
    return templates.TemplateResponse("registro_pacientes.html", {"request": request})

@app.post("/registro-pacientes", response_class=HTMLResponse)
def guardar_paciente(
    request: Request,
    rut: str = Form(...),
    nombre: str = Form(...),
    apellido_paterno: str = Form(...),
    apellido_materno: str = Form(""),
    edad: int = Form(...),
    direccion: str = Form(...),
    comuna: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    diagnostico: str = Form(""),  # ← nuevo campo
    receta: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    ...
    paciente = Paciente(
        rut=rut,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        edad=edad,
        direccion=direccion,
        comuna=comuna,
        correo=correo,
        telefono=telefono,
        diagnostico=diagnostico  # ← nuevo campo
    )


@app.get("/registro-encargado", response_class=HTMLResponse)
def mostrar_formulario_encargado(request: Request):
    return templates.TemplateResponse("registro_encargado.html", {"request": request})

@app.get("/sucursales", response_class=HTMLResponse)
async def get_sucursales(request: Request):
    return templates.TemplateResponse("sucursales.html", {"request": request})
    




@app.get("/ver-tratamiento", response_class=HTMLResponse)
def mostrar_ver_tratamiento(request: Request):
    return templates.TemplateResponse("ver_tratamiento.html", {"request": request})

@app.get("/tratamiento-paciente", response_class=HTMLResponse)
def mostrar_tratamiento_paciente(request: Request):
    return templates.TemplateResponse("tratamiento_paciente.html", {"request": request})

@app.get("/catalogo", response_class=HTMLResponse)
def mostrar_catalogo(request: Request):
    return templates.TemplateResponse("catalogo.html", {"request": request})

@app.get("/farmacias", response_class=HTMLResponse)
def mostrar_formulario_farmacias(request: Request):
    return templates.TemplateResponse("farmacias.html", {"request": request})

@app.get("/ver-vencimientos", response_class=HTMLResponse)
def mostrar_vencimientos(request: Request):
    return templates.TemplateResponse("ver_vencimientos.html", {"request": request})

@app.get("/catalogo/carga-masiva", response_class=HTMLResponse)
def mostrar_carga_masiva(request: Request):
    return templates.TemplateResponse("carga_masiva.html", {"request": request})

@app.get("/catalogo/mantenedor", response_class=HTMLResponse)
def mostrar_mantenedor_productos(request: Request):
    return templates.TemplateResponse("mantenedor_productos.html", {"request": request})

@app.get("/listado-pacientes", response_class=HTMLResponse)
async def listado_pacientes(request: Request):
    return templates.TemplateResponse("listado_pacientes.html", {"request": request})
    
@app.get("/pacientes", response_class=HTMLResponse)
async def mostrar_formulario_pacientes_unificado(request: Request):
    return templates.TemplateResponse("pacientes.html", {"request": request})

@app.get("/tratamiento", response_class=HTMLResponse)
def mostrar_tratamiento(request: Request):
    return templates.TemplateResponse("tratamiento_paciente.html", {"request": request})

@app.post("/setup-inicial")
def setup_inicial(db: Session = Depends(get_db)):
    # Verificar si ya existe una farmacia
    if db.query(Farmacia).first():
        return {"mensaje": "Ya hay registros, no se puede ejecutar nuevamente."}

    # Crear farmacia
    farmacia = Farmacia(
        rut="99999999-9",
        razon_social="Farmacia Central",
        direccion="Dirección de ejemplo",
        region="Región Metropolitana",
        comuna="Santiago",
        telefono="123456789",
        correo="admin@farmacia.cl"
    )
    db.add(farmacia)
    db.commit()
    db.refresh(farmacia)

    # Crear sucursal
    sucursal = Sucursal(
        id_farmacia=farmacia.id,
        nombre="Sucursal Central",
        direccion="Dirección Central",
        telefono="123456789",
        correo="sucursal@farmacia.cl"
    )
    db.add(sucursal)
    db.commit()
    db.refresh(sucursal)

    # Crear usuario admin
    admin = Usuario(
        nombre="Administrador",
        usuario="admin",
        contrasena="admin123",  # Puedes luego hashearla
        rol="admin",
        id_sucursal=sucursal.id_sucursal
    )
    db.add(admin)
    db.commit()

    return {"mensaje": "✅ Setup inicial completado con éxito"}




# -----------------------
# Crear Tablas
# -----------------------
Base.metadata.create_all(bind=engine)
