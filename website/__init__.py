from __future__ import annotations
from flask import Flask

# Flask Extension Modules
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_login import LoginManager
from utils import errhandler, syshandler

# Config Files
from config import Default, Development, Production

# Other Packages
from datetime import datetime
from dotenv import load_dotenv
import os

# Loading Environment Variables
load_dotenv()

# Alembic Naming
namingConvention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Metadata Object
meta = MetaData(naming_convention=namingConvention)

# SQLAlchemy Object
db = SQLAlchemy(metadata=meta)

# Login Manager Object
login_manager = LoginManager()

# Variables & Objects Available for Import
__all__ = ['db', 'loginManager', 'migrate', 'create_app']

# App Factory
def create_app(FLASK_MODE: str | None = None) -> Flask:
    # Flask Access Mode
    mode = (str(FLASK_MODE) or str(os.getenv("FLASK_MODE")) or "").strip().lower()

    # Flask Object
    app = Flask(__name__)

    # Production Configuration
    if mode == "production":
        app.config.from_object(Production)

    # Development Configuration
    elif mode == "development":
        app.config.from_object(Development)

    # Undefined App Access
    else:
        app.config.from_object(Default)

    # Importing Blueprints
    from website.modules.routes import routes

    # Registering Blueprints
    app.register_blueprint(routes, url_prefix="/")

    return app