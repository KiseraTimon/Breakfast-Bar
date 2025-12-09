from flask import Blueprint

# Blueprint Object
routes = Blueprint("routes", __name__)

# Route Files
from website.modules.routes import views