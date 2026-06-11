"""Email service — SMTP channel adapter (Fase 3: add other ChannelProvider subclasses)."""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.services.crypto_service import decrypt


class EmailService:

    def send(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password_encrypted: str,
        from_name: str,
        from_email: str,
        to_email: str,
        subject: str,
        body_html: str,
    ) -> None:
        password = decrypt(smtp_password_encrypted)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            server.login(smtp_user, password)
            server.sendmail(from_email, to_email, msg.as_string())

    def send_test(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password_encrypted: str,
        from_name: str,
        from_email: str,
    ) -> None:
        self.send(
            smtp_host, smtp_port, smtp_user, smtp_password_encrypted,
            from_name, from_email, from_email,
            "Prueba de conexión — Sistema de notificaciones",
            "<p style='font-family:sans-serif'>La configuración de correo está funcionando correctamente.</p>",
        )
