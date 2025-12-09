from flask import Flask


# App Factory
def create_app() -> Flask:
    # Flask Object
    app = Flask(__name__)

    # Importing Blueprints
    from website.modules.routes import routes

    # Registering Blueprints
    app.register_blueprint(routes, url_prefix="/")

    return app