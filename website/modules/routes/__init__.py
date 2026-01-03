from flask import Blueprint, render_template

# Blueprint Object
routes = Blueprint("routes", __name__)

# Route Files
from website.modules.routes import views
from website.modules.routes import portal