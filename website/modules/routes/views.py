from website.modules.routes import *

# Homepage Route
@routes.route("/")
def homepage():
    return render_template("home/index.html")