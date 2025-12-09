# Modules
import traceback
from datetime import datetime
import re
import os
import logging
from logging import FileHandler
import mimetypes
import zipfile
from urllib.parse import quote


try:
    from flask import request, has_request_context
except Exception:
    request = None
    def has_request_context() -> bool:
        return False

# Logging Bootstrap
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Formatter
class NewFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = getattr(request, "url", None) if request else None
            record.remote = getattr(request, "remote_addr", None) if request else None
        else:
            record.url = None
            record.remote = None
        return super().format(record)

# File Format
fileFormat = NewFormatter(
    "**********\nREMOTE: %(remote)s\nSOURCE: %(url)s\nTIME: %(asctime)s\nTYPE: %(levelname)s\nMESSAGE: %(message)s\n",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console Format
consoleFormat = NewFormatter(
    "[%(asctime)s] ||  %(levelname)s || %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


# Terminal Messenger
class TerminalMessenger:
    @staticmethod
    def message(text):
        console = logging.StreamHandler()
        console.setFormatter(fileFormat)
        logger.addHandler(console)
        try:
            logger.info(text)
        finally:
            logger.removeHandler(console)


# Timestamp
class TimeUtils:
    @staticmethod
    def timestp():
        now = datetime.now()
        return now.strftime("%d-%m-%Y %H:%M:%S")

# Error Utilities
class ErrorUtils:
    @staticmethod
    def error(e):
        # Extracting Error Type
        err_type = type(e).__name__

        # Extracting Error Message
        err_msg = str(e)

        # Traceback List
        tb_list = traceback.extract_tb(e.__traceback__) if getattr(e, "__traceback__", None) else []

        # Extracting Filename & Line Number
        if tb_list:
            tb = tb_list[-1]
            filename = tb.filename
            line_no = tb.lineno
        else:
            filename = None
            line_no = None

        # Error Details
        error_details = (
            f"ERROR TYPE:\n{err_type}\n\n"
            f"ERROR MESSAGE:\n{err_msg if err_msg else None}\n\n"
            f"ERROR ORIGIN:\n{filename}\n\n"
            f"ERROR LINE:\n{line_no}"
        )

        return error_details


# Error Logger
class ErrorHandler:
    @staticmethod
    def errhandler(e = None, log = None, path = None):

        # Building Path to Log Error
        if path is not None:
            os.makedirs(f"logs/errors/{path}", exist_ok=True)
            logFile = f"{path}/{log}"
            file_path = f"logs/errors/{logFile}.log"
        else:
            os.makedirs("logs/errors", exist_ok=True)
            logFile = log
            file_path = f"logs/errors/{logFile}.log"

        # Building Error Text
        time_str = TimeUtils.timestp()
        error_details = ErrorUtils.error(e)
        header_line = f"CRITICAL ERROR @ {time_str}. CHECK *{logFile.upper()}* LOGS\n\n"

        # Terminal Error Logging
        console = logging.StreamHandler()
        console.setFormatter(consoleFormat)
        logger.addHandler(console)
        try:
            logger.error(header_line)
        finally:
            logger.removeHandler(console)

        # Storing Error Log
        file_handler = FileHandler(file_path, mode="a")
        file_handler.setFormatter(fileFormat)
        logger.addHandler(file_handler)
        try:
            logger.error(
                f"\n--------------------------------------------------\n"
                f"{error_details}\n---\n"
                f"--------------------------------------------------\n\n"
            )
        finally:
            logger.removeHandler(file_handler)


# System Logger
class SystemLogger:
    @staticmethod
    def syshandler(msg = None, log = None, path = None):

        # Building Path to Log Message
        if path is not None:
            os.makedirs(f"logs/system/{path}", exist_ok=True)
            logFile = f"{path}/{log}"
            file_path = f"logs/system/{logFile}.log"
        else:
            os.makedirs("logs/system", exist_ok=True)
            logFile = log
            file_path = f"logs/system/{logFile}.log"

        time_str = TimeUtils.timestp()
        header_line = f"SYSTEM INFORMATION @ {time_str}. CHECK *{logFile.upper()}*\n\n"

        # Terminal Message Logging
        console = logging.StreamHandler()
        console.setFormatter(consoleFormat)
        logger.addHandler(console)
        try:
            logger.info(header_line)
        finally:
            logger.removeHandler(console)

        # Storing Message Log
        file_handler = FileHandler(file_path, mode="a")
        file_handler.setFormatter(fileFormat)
        logger.addHandler(file_handler)
        try:
            logger.info(
                f"\n--------------------------------------------------\n"
                f"{msg}\n---\n"
                f"--------------------------------------------------\n\n"
            )
        finally:
            logger.removeHandler(file_handler)


class MailService:
    @staticmethod
    def _bool_env(name, fallback=False):
        val = str(os.getenv(name, str(fallback))).strip().lower()
        return val in {"1", "true", "yes", "on"}

    @staticmethod
    def mailer(recipient, subject, **kwargs):
        if not subject or not recipient:
            return False

        try:
            from settings import env
        except ImportError:
            env = None

        # Message
        sender = kwargs.get(
            "sender",
            os.getenv("MAIL_DEFAULT_SENDER") or getattr(env, "MAIL_DEFAULT_SENDER", None)
        )
        body = kwargs.get("body", None)
        html = kwargs.get("html", None)

        # Build email
        from email.message import EmailMessage
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

        # Attempting to Send Mail
        try:
            import smtplib
            if use_ssl:
                with smtplib.SMTP_SSL(host=host, port=port) as smtp:
                    if username and password:
                        smtp.login(username, password)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(host=host, port=port) as smtp:
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
        else:
            SystemLogger.syshandler(f"System-generated mail to '{recipient}'", log="mailer", path="utils")
            return True

class ZipService:
    @staticmethod
    def zipfilehandler(filePath, outputDir, **kwargs):
        os.makedirs(outputDir, exist_ok=True)

        client = kwargs.get("client", None)

        ts = datetime.now().strftime("%Y%m%d%H%M%S")

        if client:
            zip_filename = f"{ts}_{client + '_'}.zip"
        else:
            zip_filename = f"{ts}_AuditFile.zip"
        zip_path = os.path.join(outputDir, zip_filename)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for fp in filePath:
                if os.path.exists(fp):
                    zipf.write(fp, os.path.basename(fp))

        return zip_filename, zip_path


class FilenameUtils:
    @staticmethod
    def stripPrefix(filename):
        return "_".join(filename.split("_")[1:]) if "_" in filename else filename

    @staticmethod
    def cleanFilename(filename):
        filename = os.path.basename(filename)
        filename = re.sub(r"[^\w\-.]", "_", filename)
        return filename


class FileService:
    @staticmethod
    def filehandler(**kwargs):
        item = kwargs.get("item", None)
        itemType = kwargs.get("type", "image")
        path = kwargs.get("path", "uploads")
        subPath = kwargs.get("subPath", "undefined")
        operation = kwargs.get("operation", None)

        DEFAULT_ITEM_PATH = os.path.join("website", "static", "uploads", "item-not-found.png")

        if not item:
            return DEFAULT_ITEM_PATH.replace("\\", "/")

        # Processing Images
        if itemType == "image":
            UPLOAD_FOLDER = os.path.join("website", "static", path, "images", subPath)
            ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

        # Processing Files
        elif itemType == "file":
            UPLOAD_FOLDER = os.path.join("website", "static", path, "files", subPath)
            ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "zip", "pdf", "csv", "7zip", "rar", "docx", "xlsx"}

        # Processing Undefined File Types
        else:
            SystemLogger.syshandler(f"Unknown itemType '{itemType}'", log="imghandler", path="utils")
            return DEFAULT_ITEM_PATH.replace("\\", "/")

        # Processing by Operation
        if operation is None or operation == "add":
            try:
                if item and hasattr(item, "filename") and item.filename != "":
                    # Extension Check
                    if "." not in item.filename or item.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
                        SystemLogger.syshandler("Invalid image/file extension", log="imghandler", path="utils")
                        return DEFAULT_ITEM_PATH.replace("\\", "/")

                    # Renaming
                    filename = FilenameUtils.cleanFilename(item.filename)
                    ts = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{ts}_{filename}"

                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    # Saving Item
                    item.save(save_path)

                    return save_path.replace("\\", "/")

                return DEFAULT_ITEM_PATH.replace("\\", "/")

            except Exception as e:
                ErrorHandler.errhandler(e, log="imghandler", path="utils")
                return DEFAULT_ITEM_PATH.replace("\\", "/")

        # Future operations could be added here (e.g., delete/replace)
        return DEFAULT_ITEM_PATH.replace("\\", "/")


# Backward Compatible Function Proxies

def message(text):
    return TerminalMessenger.message(text)

def timestp():
    return TimeUtils.timestp()

def error(e):
    return ErrorUtils.error(e)

def errhandler(e, log, **kwargs):
    return ErrorHandler.errhandler(e, log, **kwargs)

def syshandler(msg, log, **kwargs):
    return SystemLogger.syshandler(msg, log, **kwargs)

def mailer(recipient, subject, **kwargs):
    return MailService.mailer(recipient, subject, **kwargs)

def zipfilehandler(filePath, outputDir, **kwargs):
    return ZipService.zipfilehandler(filePath, outputDir, **kwargs)

def stripPrefix(filename):
    return FilenameUtils.stripPrefix(filename)

def cleanFilename(filename):
    return FilenameUtils.cleanFilename(filename)

def filehandler(**kwargs):
    return FileService.filehandler(**kwargs)
