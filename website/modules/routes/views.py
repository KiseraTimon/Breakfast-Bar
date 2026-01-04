from website.modules.routes import *

# Homepage Route
@routes.route("/")
def homepage():
    return render_template("home/index.html")

# Menu Route
@routes.route("/menu")
def menu():
    return render_template("menu/menu.html")

# Food Details
@routes.route("/item")
def food():
    return render_template("menu/food-details.html")

# Services Route
@routes.route("/services")
def services():
    return render_template("services/services.html")