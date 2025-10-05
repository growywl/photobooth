from flask import Flask

from . import config
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.register_blueprint(bp)
    return app
