from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tratamiento, Paciente
from datetime import date, timedelta

def get_tratamientos_proximos_a_vencer():
    from app.database import SessionLocal
    db: Session = SessionLocal()
    try:
        hoy = date.today()
        resultados = (
            db.query(
                Tratamiento.rut_paciente,
                Tratamiento.nombre_medicamento,
                Tratamiento.fecha_fin,
                Paciente.nombre.label("nombre_paciente"),
                Paciente.correo,
                Paciente.telefono,
                Paciente.direccion,
                Paciente.comuna
            )
            .join(Paciente, Tratamiento.rut_paciente == Paciente.rut)
            .filter(Tratamiento.fecha_fin >= hoy)
            .filter(Tratamiento.fecha_fin <= hoy.replace(day=hoy.day + 5))  # tratamientos que vencen en 5 días
            .all()
        )
        return [
            {
                "rut_paciente": r.rut_paciente,
                "nombre_medicamento": r.nombre_medicamento,
                "fecha_fin": r.fecha_fin,
                "dias_restantes": (r.fecha_fin - hoy).days,
                "nombre_paciente": r.nombre_paciente,
                "correo": r.correo,
                "telefono": r.telefono,
                "direccion": r.direccion,
                "comuna": r.comuna
            }
            for r in resultados
        ]
    finally:
        db.close()