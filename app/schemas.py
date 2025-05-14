from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from pydantic import BaseModel, constr
from datetime import date
import datetime
from typing import List

# --- Sucursal ---
class SucursalBase(BaseModel):
    nombre: str
    direccion: str
    region: str
    comuna: str
    telefono: str
    correo: str  # <--- nuevo campo agregado
    id_farmacia: int

class SucursalConEncargadoCreate(SucursalBase):
    encargado_rut: str
    encargado_nombre: str
    encargado_telefono: str
    encargado_correo: str
    
class SucursalEncargadoSchema(BaseModel):
    id_farmacia: int
    nombre: str
    direccion: str
    comuna: str
    region: str
    telefono: str = None
    correo_sucursal: str = None
    rut_encargado: str = None
    nombre_encargado: str = None
    telefono_encargado: str = None
    correo_encargado: str = None

class SucursalCreate(SucursalBase):
    pass

class SucursalResponse(SucursalBase):
    id: int

    class Config:
        from_attributes = True

# --- Usuario ---
class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    contrasena: str
    rol: str
    sucursal_id: int

from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: constr(max_length=40)
    usuario: constr(min_length=3, max_length=30)
    contrasena: Optional[constr(min_length=6, max_length=12)] = None  # ← AHORA OPCIONAL
    rut: constr(max_length=10)
    telefono: constr(min_length=9, max_length=9)
    rol: str
    id_sucursal: int
    id_farmacia: int


class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

# --- Farmacia ---
class FarmaciaBase(BaseModel):
    rut: str
    razon_social: str
    direccion: str
    region: str
    comuna: str
    telefono: str
    correo: EmailStr
    encargado_rut: Optional[str] = None
    encargado_nombre: Optional[str] = None
    encargado_telefono: Optional[str] = None
    encargado_correo: Optional[EmailStr] = None

    
class FarmaciaConEncargadoResponse(BaseModel):
    id: int
    rut: str
    razon_social: str
    direccion: str
    region: str
    comuna: str
    telefono: str
    correo: str
    encargado_rut: Optional[str]
    encargado_nombre: Optional[str]
    encargado_telefono: Optional[str]
    encargado_correo: Optional[str]

    class Config:
        from_attributes = True


class FarmaciaCreate(FarmaciaBase):
    pass

class FarmaciaResponse(FarmaciaBase):
    id: int

    class Config:
        from_attributes = True

class PacienteBase(BaseModel):
    rut: str
    nombre: str
    fecha_nacimiento: date
    edad: int
    direccion: str
    comuna: str
    region: str
    telefono: str
    correo: str
    diagnostico: Optional[str]  # ← nuevo campo

class PacienteCreate(PacienteBase):
    pass

class EncargadoOut(BaseModel):
    rut_encargado: str
    nombre: str
    apellidos: str = ""  # si no estás usando esto, elimínalo
    direccion: str
    comuna: str
    parentesco: str
    telefono: str
    correo: str
    rut_paciente: str

    class Config:
        from_attributes = True
  
class PacienteCreate(BaseModel):
    rut: str
    nombre: str
    fecha_nacimiento: date
    edad: int
    direccion: str
    comuna: str
    region: str
    telefono: str
    correo: str
    diagnostico: Optional[str]

class PacienteResponse(PacienteBase):
    model_config = {
        "from_attributes": True
    }

# --- Tratamiento ---
class TratamientoBase(BaseModel):
    rut_paciente: str
    nombre_medicamento: str
    cantidad_por_caja: int
    dosis_diaria: int
    duracion_dias: int
    fecha_fin: datetime.date

class TratamientoCreate(TratamientoBase):
    pass

class TratamientoResponse(BaseModel):
    id: int
    rut_paciente: str
    nombre_medicamento: str
    codigo_barra: str | None = None
    principio_activo: str | None = None  # ✅ AGREGAR
    laboratorio: str | None = None       # ✅ AGREGAR
    precio_venta: float | None = None    # ✅ AGREGAR
    cantidad_por_caja: int
    dosis_diaria: int
    duracion_dias: int
    fecha_fin: date

    class Config:
       from_attributes = True

class ProductoBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    principio_activo: Optional[str] = Field(None, max_length=100)
    laboratorio: str = Field(..., max_length=100)
    formato: str = Field(..., max_length=50)
    precio_compra_neto: int
    precio_venta_neto: int
    precio_venta: int

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class ProductoResponse(BaseModel):
    # id: int  ← ✂️ elimina esta línea
    codigo: str
    nombre: str
    principio_activo: str
    laboratorio: str
    formato: str
    precio_compra_neto: int
    precio_venta_neto: int
    precio_venta: int

    class Config:
        from_attributes = True

class ProductoOut(BaseModel):
    # id: int  ← ✂️ elimina esta línea
    codigo: str
    nombre: str
    principio_activo: Optional[str] = None
    laboratorio: Optional[str] = None
    formato: Optional[str] = None
    precio_compra_neto: Optional[float] = None
    precio_venta_neto: Optional[float] = None
    precio_venta: Optional[float] = None

    class Config:
        from_attributes = True
        
class EncargadoCreate(BaseModel):
    rut_encargado: str
    nombre: str
    direccion: Optional[str]
    comuna: Optional[str]
    parentesco: Optional[str]
    telefono: Optional[str]
    correo: Optional[str]
    rut_paciente: str

    model_config = {
        'from_attributes': True
    }

# app/schemas.py
class ContactoSchema(BaseModel):
    rut_paciente: str
    nombre_medicamento: str
    tipo_contacto: str
    usuario: str

class UsuarioLogin(BaseModel):
    usuario: str
    contrasena: str
   

class ContactoResponse(BaseModel):
    rut_paciente: str
    nombre_medicamento: str
    tipo_contacto: str
    fecha_contacto: datetime.datetime
    usuario: str

    class Config:
        from_attributes = True