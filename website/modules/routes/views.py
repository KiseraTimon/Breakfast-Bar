from website.modules.routes import *

# Homepage Route
@routes.route("/")
def homepage():
    return render_template("home/index.html")

# Menu Route
@routes.route("/menu")
def menu():
    return render_template("menu/menu.html")

# Services Route
@routes.route("/services")
def services():
    return render_template("services/services.html")