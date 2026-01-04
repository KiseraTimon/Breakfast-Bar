from . import routes, render_template

# Dashboard Route
@routes.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")

# Admin Dashboard Route
@routes.route("/administrator")
def admin():
    return render_template("dashboard/admin.html")