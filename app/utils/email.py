import smtplib
from email.mime.text import MIMEText

def enviar_correo(destinatario: str, asunto: str, cuerpo: str, remitente: str, clave_app: str, servidor="smtp.gmail.com", puerto=587):
    mensaje = MIMEText(cuerpo, 'html')
    mensaje['Subject'] = asunto
    mensaje['From'] = remitente
    mensaje['To'] = destinatario

    server = smtplib.SMTP(servidor, puerto)
    server.starttls()
    server.login(remitente, clave_app)
    server.sendmail(remitente, destinatario, mensaje.as_string())
    server.quit()
