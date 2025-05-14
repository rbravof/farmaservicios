from fastapi import APIRouter
from app.routers.reporte_vencimientos_diario import generar_excel_y_enviar

router = APIRouter()

@router.get("/test-reporte")
def test_envio_correo():
    generar_excel_y_enviar()
    return {"status": "✅ Correo enviado manualmente"}
