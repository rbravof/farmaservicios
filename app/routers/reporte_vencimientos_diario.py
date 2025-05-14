import pandas as pd
import smtplib
from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.utils.db_queries import get_tratamientos_proximos_a_vencer # deberías tener esta función
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("CORREO_ORIGEN")
EMAIL_PASS = os.getenv("CLAVE_CORREO")

def generar_excel_y_enviar():
    print(f"[{datetime.now()}] Iniciando generación de reporte de vencimientos...")

    try:
        tratamientos = get_tratamientos_proximos_a_vencer()

        print("Tratamientos obtenidos:")
        for t in tratamientos:
            print(t)


        if not tratamientos:
            print(f"[{datetime.now()}] ❌ No hay tratamientos próximos a vencer.")
            return

        df = pd.DataFrame(tratamientos)
        archivo = f"vencimientos_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(archivo, index=False)
        print(f"[{datetime.now()}] ✅ Archivo Excel generado: {archivo}")

        msg = EmailMessage()
        msg['Subject'] = '📋 Reporte de Tratamientos por Vencer'
        msg['From'] = EMAIL_USER
        msg['To'] = 'rbravofuentes@gmail.com'
        msg.set_content("Adjunto se encuentra el reporte diario de tratamientos próximos a vencer.")

        with open(archivo, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=archivo)

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
            print(f"[{datetime.now()}] 📬 Correo enviado con éxito a {msg['To']}")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error al generar o enviar el reporte: {e}")


# Programar para que se ejecute todos los días a las 07:00
scheduler = BackgroundScheduler()
scheduler.add_job(generar_excel_y_enviar, 'cron', hour=10, minute=7)
scheduler.start()
