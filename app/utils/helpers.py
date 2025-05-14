from datetime import datetime

def formatear_fecha(fecha: datetime, formato: str = "%d-%m-%Y") -> str:
    return fecha.strftime(formato)

def calcular_edad(fecha_nacimiento: datetime) -> int:
    today = datetime.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def limpiar_texto(texto: str) -> str:
    return texto.strip().replace("\n", " ").replace("\r", " ")
