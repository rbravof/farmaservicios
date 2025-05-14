from sqlalchemy import Column, String, Integer, ForeignKey, Float, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from app.database import Base
from datetime import datetime
from datetime import date
from app import models

class Sucursal(Base):
    __tablename__ = "sucursales"

    id_sucursal = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(120), nullable=False)
    region = Column(String(50), nullable=False)
    comuna = Column(String(50), nullable=False)
    telefono = Column(String(9))
    correo_sucursal = Column(String(50), nullable=True)
    id_farmacia = Column(Integer, ForeignKey("farmacias.id"), nullable=False)

    farmacia = relationship("Farmacia", back_populates="sucursales")
    encargado = relationship("SucEncargado", back_populates="sucursal", uselist=False)
    usuarios = relationship("Usuario", back_populates="sucursal")

    
class SucEncargado(Base):
    __tablename__ = "suc_encargado"

    id_encargado = Column(Integer, primary_key=True, index=True)
    rut_encargado = Column(String(10), nullable=False)
    nombre_encargado = Column(String(80), nullable=False)
    telefono_encargado = Column(String(9))
    correo_encargado = Column(String(50))
    id_sucursal = Column(Integer, ForeignKey("sucursales.id_sucursal"), nullable=False, unique=True)

    sucursal = relationship("Sucursal", back_populates="encargado")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(40), nullable=False)
    usuario = Column(String(30), unique=True, nullable=False)
    contrasena = Column(String(128), nullable=False)
    rut = Column(String(10), unique=True, nullable=False)
    telefono = Column(String(9), nullable=False)
    rol = Column(String(50), nullable=False)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id_sucursal"), nullable=False)

    sucursal = relationship("Sucursal", back_populates="usuarios")  # ✅ ESTA LÍNEA

class Farmacia(Base):
    __tablename__ = "farmacias"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, nullable=False)
    razon_social = Column(String(100), nullable=False)
    direccion = Column(String(150))
    comuna = Column(String(50))
    region = Column(String(50))
    telefono = Column(String(15))
    correo = Column(String(100))
    
    # 👇 Agrega estos campos que sí existen en la base de datos
    encargado_rut = Column(String(12), nullable=True)
    encargado_nombre = Column(String(100), nullable=True)
    encargado_telefono = Column(String(15), nullable=True)
    encargado_correo = Column(String(150), nullable=True)

    sucursales = relationship("Sucursal", back_populates="farmacia")


class Paciente(Base):
    __tablename__ = "pacientes"

    rut = Column(String, primary_key=True, index=True)
    nombre = Column(String(90))
    fecha_nacimiento = Column(Date)
    edad = Column(Integer)
    direccion = Column(String(120))
    comuna = Column(String(50))
    region = Column(String(50))
    telefono = Column(String(9))
    correo = Column(String(100))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    diagnostico = Column(String(200))  # ← nuevo campo

    tratamientos = relationship("Tratamiento", back_populates="paciente")
    encargado = relationship("Encargado", uselist=False, back_populates="paciente")
    contactos = relationship("Contacto", back_populates="paciente")

class Tratamiento(Base):
    __tablename__ = "tratamientos"

    id = Column(Integer, primary_key=True, index=True)
    rut_paciente = Column(String, ForeignKey("pacientes.rut"), nullable=False)
    nombre_medicamento = Column(String)
    codigo_barra = Column(String)
    cantidad_por_caja = Column(Integer)
    dosis_diaria = Column(Integer)
    duracion_dias = Column(Integer)
    fecha_inicio = Column(Date)  # 👈 NUEVA COLUMNA
    fecha_fin = Column(Date)

    paciente = relationship("Paciente", back_populates="tratamientos")


class Producto(Base):
    __tablename__ = "productos"

    codigo = Column(String(50), primary_key=True, index=True)  # ← esta ya es clave primaria
    nombre = Column(String(150), nullable=False)
    principio_activo = Column(String(100))
    laboratorio = Column(String(100))
    formato = Column(String(50))
    precio_compra_neto = Column(Integer)
    precio_venta_neto = Column(Integer)
    precio_venta = Column(Integer)

    
class Encargado(Base):
    __tablename__ = "encargados"

    rut_encargado = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(90), nullable=False)
    direccion = Column(String(120))
    comuna = Column(String(60))
    parentesco = Column(String(30))
    telefono = Column(String(9))
    correo = Column(String(100))
    rut_paciente = Column(String(10), ForeignKey("pacientes.rut"), nullable=False)
    
    paciente = relationship("Paciente", back_populates="encargado")

class TratamientoXvencer(Base):
    __tablename__ = "tratamientos_x_vencer"

    id = Column(Integer, primary_key=True, index=True)
    rut_paciente = Column(String, index=True)
    nombre_paciente = Column(String)
    nombre_medicamento = Column(String)
    fecha_fin = Column(Date)
    dias_restantes = Column(Integer)
    correo_enviado = Column(Boolean, default=False)
    whatsapp_enviado = Column(Boolean, default=False)
    
# app/models.py
class Contacto(Base):
    __tablename__ = "contactos"

    id = Column(Integer, primary_key=True, index=True)
    rut_paciente = Column(String, ForeignKey("pacientes.rut"), nullable=False)
    nombre_medicamento = Column(String, nullable=False)
    tipo_contacto = Column(String, nullable=False)  # 'correo' o 'whatsapp'
    fecha_contacto = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String, nullable=False)

    paciente = relationship("Paciente", back_populates="contactos")

class HistTratamiento(Base):
    __tablename__ = "hist_tratamientos"

    id = Column(Integer, primary_key=True, index=True)
    rut_paciente = Column(String, nullable=False)
    nombre_medicamento = Column(String, nullable=False)
    fecha_inicio = Column(Date, nullable=False)  # 👈 ESTA LÍNEA ES OBLIGATORIA
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String, nullable=False)
    fecha_historico = Column(DateTime, default=datetime.now, nullable=False)
    codigo_barra = Column(String)
    dosis_diaria = Column(Integer)
    cantidad_por_caja = Column(Integer)
    fecha_fin_real = Column(Date)

