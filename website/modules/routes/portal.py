from website.modules.routes import *

# Dashboard Route
@routes.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")

# Admin Dashboard Route
@routes.route("/administrator")
def admin():
    return render_template("dashboard/admin.html")