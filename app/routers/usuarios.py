from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.utils.utils import send_reset_email
from app.schemas import UsuarioLogin
from app.schemas import UsuarioCreate
from app.models import Usuario, Sucursal, Farmacia
from app.database import get_db
import uuid
from datetime import datetime, timedelta
import bcrypt

router = APIRouter()

@router.get("/usuarios/reestablecer-password/{token}", response_class=HTMLResponse)
async def mostrar_formulario_reestablecer(token: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT correo, expiracion FROM tokens_recuperacion WHERE token = %s", (token,))
    token_data = cursor.fetchone()

    if not token_data or token_data[1] < datetime.now():
        return HTMLResponse("<h2>⚠️ El enlace ha expirado o no es válido.</h2>", status_code=400)

    html_form = f"""
    <html>
    <head>
        <title>Reestablecer Contraseña</title>
        <style>
            body {{
                font-family: 'Segoe UI';
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f4f6f8;
            }}
            .form-container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
            }}
            input {{
                display: block;
                width: 100%;
                padding: 10px;
                margin-top: 10px;
                margin-bottom: 20px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }}
            button {{
                padding: 10px 20px;
                background: #00796B;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>🔒 Reestablecer Contraseña</h2>
            <form method="post">
                <input type="password" name="nueva_password" placeholder="Nueva contraseña" required>
                <input type="hidden" name="token" value="{token}">
                <button type="submit">Actualizar</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_form)

@router.post("/usuarios/reestablecer-password/{token}", response_class=HTMLResponse)
async def procesar_reestablecer_password(token: str, nueva_password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT correo FROM tokens_recuperacion WHERE token = %s AND expiracion > %s", (token, datetime.now()))
    result = cursor.fetchone()

    if not result:
        return HTMLResponse("<h2>⚠️ El enlace no es válido o ha expirado.</h2>", status_code=400)

    correo = result[0]
    hashed_password = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("UPDATE usuarios SET contrasena = %s WHERE correo = %s", (hashed_password, correo))
    cursor.execute("DELETE FROM tokens_recuperacion WHERE token = %s", (token,))
    conn.commit()

    return HTMLResponse("<h2>✅ Tu contraseña ha sido actualizada correctamente.</h2>")

@router.post("/crear")
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verificar que el nombre de usuario no exista
    db_usuario = db.query(Usuario).filter(Usuario.usuario == usuario.usuario).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

    # 2. Hashear la contraseña
    hashed_password = bcrypt.hashpw(usuario.contrasena.encode('utf-8'), bcrypt.gensalt())

    # 3. Crear nuevo usuario
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        usuario=usuario.usuario,
        contrasena=hashed_password.decode('utf-8'),
        rut=usuario.rut,
        telefono=usuario.telefono,
        rol=usuario.rol,
        id_sucursal=usuario.id_sucursal
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"mensaje": "Usuario creado exitosamente", "id_usuario": nuevo_usuario.id}

@router.delete("/eliminar/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()

    return {"mensaje": "Usuario eliminado correctamente"}

@router.post("/recuperar-password")
async def solicitar_recuperacion_password(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    correo = data.get("correo")

    if not correo:
        raise HTTPException(status_code=400, detail="Correo requerido")

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="No se encontró un usuario con ese correo")

    token = str(uuid.uuid4())
    usuario.token_recuperacion = token
    usuario.token_expira = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    send_reset_email(correo, token)

    return {"message": "Correo enviado para recuperar la contraseña."}

@router.get("/todos")
def listar_todos_los_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).join(Sucursal, Usuario.id_sucursal == Sucursal.id_sucursal).join(
        Farmacia, Sucursal.id_farmacia == Farmacia.id
    ).all()

    resultado = []
    for usuario in usuarios:
        resultado.append({
            "id": usuario.id,
            "rut": usuario.rut,
            "nombre": usuario.nombre,  # 👈 aquí estaba faltando o mal nombrado
            "telefono": usuario.telefono,
            "usuario": usuario.usuario,
            "rol": usuario.rol,
            "nombre_farmacia": usuario.sucursal.farmacia.razon_social,
            "nombre_sucursal": usuario.sucursal.nombre
        })

    return resultado

@router.get("/por-farmacia/{id_farmacia}")
def listar_usuarios_por_farmacia(id_farmacia: int, db: Session = Depends(get_db)):
    resultados = (
        db.query(
            Usuario.id,
            Usuario.usuario,
            Usuario.rut,
            Usuario.telefono,
            Usuario.rol,
            Sucursal.nombre.label("nombre_sucursal"),
            Farmacia.razon_social.label("nombre_farmacia")
        )
        .join(Sucursal, Usuario.id_sucursal == Sucursal.id_sucursal)
        .join(Farmacia, Sucursal.id_farmacia == Farmacia.id)
        .filter(Sucursal.id_farmacia == id_farmacia)
        .all()
    )

    return [dict(row._mapping) for row in resultados]



@router.put("/editar/{id_usuario}")
def editar_usuario(id_usuario: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_usuario.nombre = usuario.nombre
    db_usuario.usuario = usuario.usuario
    db_usuario.rut = usuario.rut
    db_usuario.telefono = usuario.telefono
    db_usuario.rol = usuario.rol
    db_usuario.id_sucursal = usuario.id_sucursal

    if usuario.contrasena:
        hashed_password = bcrypt.hashpw(usuario.contrasena.encode('utf-8'), bcrypt.gensalt())
        db_usuario.contrasena = hashed_password.decode('utf-8')

    db.commit()

    return {"mensaje": "Usuario actualizado exitosamente"}
    
@router.get("/obtener/{id_usuario}")
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": usuario.id,
        "rut": usuario.rut,
        "nombre": usuario.nombre,
        "telefono": usuario.telefono,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "id_sucursal": usuario.id_sucursal,
        "id_farmacia": usuario.sucursal.id_farmacia  # <-- Ojo, trae farmacia a la que pertenece
    }

@router.post("/login")
def login_usuario(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.usuario == datos.usuario).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not bcrypt.checkpw(datos.contrasena.encode('utf-8'), usuario.contrasena.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "id_sucursal": usuario.id_sucursal,
        "id_farmacia": usuario.sucursal.id_farmacia,
        "nombre_sucursal": usuario.sucursal.nombre
    }