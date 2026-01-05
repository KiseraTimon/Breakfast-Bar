from __future__ import annotations
from flask import Flask

# Flask Extension Modules
from flask_migrate import Migrate
from flask_login import LoginManager
from database import db

# Config Files
from config import Default, Development, Production

# Other Packages
from utils import errhandler, syshandler
from datetime import datetime
from dotenv import load_dotenv
import os

# Migrate Object
migrate = Migrate()

# Login Manager Object
login_manager = LoginManager()

# Variables & Objects Available for Import
__all__ = ['db', 'login_manager', 'migrate', 'create_app']

# App Factory
def create_app(FLASK_MODE: str | None = None) -> Flask:
    # Loading Environment Variables
    load_dotenv()

    # Flask Access Mode
    mode = (
        FLASK_MODE
        if FLASK_MODE is not None
        else os.getenv("FLASK_MODE", "")
    ).strip().lower()

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

    # Bindings
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)

    # Login Manager Settings
    login_manager.login_view = ""
    login_manager.login_message = "Access Denied"

    login_manager.init_app(app)

    # Importing Models
    with app.app_context():
        from . import models

    # Importing Blueprints
    from website.modules.routes import routes

    # Registering Blueprints
    app.register_blueprint(routes, url_prefix="/")


    try:
        # Critical Config Keys
        config_keys = ["DEBUG", "TESTING"]
        config_summary = "\n".join(
            f"{key}: {app.config.get(key)}" for key in config_keys
        )

        syshandler(f"Application Server Start Attempted\n\n-----\nApp Settings:\n{config_summary}\nFLASK MODE: {mode.capitalize()}", log="__init__", path="server")

        return app

    except Exception as e:
        errhandler(e, log="__init__", path="server")

        # Raising Exceptions
        raise