from website.modules.routes import *

# Dashboard Route
@routes.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")