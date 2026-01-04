import os
from email.message import EmailMessage

from .error_handler import ErrorHandler
from .sys_logger import SystemLogger


class MailManager:
    @staticmethod
    def _bool_env(name, fallback=False):
        val = str(os.getenv(name, str(fallback))).strip().lower()
        return val in {"1", "true", "yes", "on"}

    @staticmethod
    def mailer(recipient, subject, **kwargs):
        if not recipient or not subject:
            return False

        try:
            from settings import env
        except ImportError:
            env = None

        sender = kwargs.get(
            "sender",
            os.getenv("MAIL_DEFAULT_SENDER") or getattr(env, "MAIL_DEFAULT_SENDER", None)
        )
        body = kwargs.get("body")
        html = kwargs.get("html")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        if html and body:
            msg.set_content(body)
            msg.add_alternative(html, subtype="html")
        elif html:
            msg.add_alternative(html, subtype="html")
        elif body:
            msg.set_content(body)
        else:
            msg.set_content("")

        host = os.getenv("MAIL_SERVER") or getattr(env, "MAIL_SERVER", "localhost")
        port = int(os.getenv("MAIL_PORT") or getattr(env, "MAIL_PORT", 25))
        username = os.getenv("MAIL_USERNAME") or getattr(env, "MAIL_USERNAME", None)
        password = os.getenv("MAIL_PASSWORD") or getattr(env, "MAIL_PASSWORD", None)

        use_tls = MailService._bool_env("MAIL_USE_TLS", getattr(env, "MAIL_USE_TLS", False))
        use_ssl = MailService._bool_env("MAIL_USE_SSL", getattr(env, "MAIL_USE_SSL", False))

        try:
            import smtplib

            if use_ssl:
                with smtplib.SMTP_SSL(host, port) as smtp:
                    if username and password:
                        smtp.login(username, password)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(host, port) as smtp:
                    smtp.ehlo()
                    if use_tls:
                        smtp.starttls()
                        smtp.ehlo()
                    if username and password:
                        smtp.login(username, password)
                    smtp.send_message(msg)

        except Exception as e:
            ErrorHandler.errhandler(e, log="mailer", path="utils")
            return False

        SystemLogger.syshandler(
            f"System-generated mail to '{recipient}'",
            log="mailer",
            path="utils"
        )
        return True
