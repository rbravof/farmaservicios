import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_reset_email(to_email: str, token: str):
    remitente = os.getenv("CORREO_ORIGEN")
    clave = os.getenv("CLAVE_CORREO")
    servidor = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
    puerto = int(os.getenv("EMAIL_PORT", 587))

    if not remitente or not clave:
        raise Exception("⚠️ Las variables de entorno CORREO_ORIGEN y CLAVE_CORREO no están definidas")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Recuperación de Contraseña - FarmaServicios"
    msg["From"] = remitente
    msg["To"] = to_email

    enlace = f"https://tusitio.cl/restablecer-clave?token={token}"
    html = f"""
    <html>
      <body>
        <p>Hola,</p>
        <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace:</p>
        <p><a href="{enlace}">Restablecer Contraseña</a></p>
        <p><small>Este enlace expirará en 1 hora.</small></p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(servidor, puerto) as server:
        server.starttls()
        server.login(remitente, clave)
        server.sendmail(remitente, to_email, msg.as_string())
