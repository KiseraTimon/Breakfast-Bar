from flask import Blueprint

# Blueprint Object
routes = Blueprint("routes", __name__)

# Route Files
from . import views, portal, auth

__all__ = ["routes"]
