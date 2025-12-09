from website.modules.routes import routes

# Homepage Route
@routes.route("/")
def homepage():
    return "Homepage is working"