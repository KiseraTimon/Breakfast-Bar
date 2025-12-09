from flask import Flask


# App Factory
def create_app() -> Flask:
    # Flask Object
    app = Flask(__name__)

    return app