from . import DB_URL, os
from .default import Default

class Development(Default):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    TESTING = False
    MAIL_SUPPRESS_SEND = False

    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"
    )

    WKHTMLTOPDF_BIN_PATH = os.getenv("WKHTMLTOPDF_BIN_PATH")

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", 10)),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 20)),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", 20)),
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 300)),
        "pool_pre_ping": os.getenv("SQLALCHEMY_POOL_PRE_PING", "True") == "True",
        "pool_use_lifo": os.getenv("SQLALCHEMY_POOL_USE_LIFO", "True") == "True",
        "echo_pool": os.getenv("SQLALCHEMY_ECHO_POOL", "False") == "True",
        "echo": os.getenv("SQLALCHEMY_ECHO", "False") == "True",
    }

    PRESERVE_CONTEXT_ON_EXCEPTION = False