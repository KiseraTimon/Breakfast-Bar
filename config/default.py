from . import os

class Default:
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False

    SECRET_KEY = os.getenv("SECRET_KEY")

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 25))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_MAX_EMAILS = os.getenv("MAIL_MAX_EMAILS")
    MAIL_ASCII_ATTACHMENTS = os.getenv("MAIL_ASCII_ATTACHMENTS") == "True"

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    BASE_URL = os.getenv("BASE_URL")