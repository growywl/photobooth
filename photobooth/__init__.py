from flask import Flask

from . import config
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # Ensure expected directories exist.
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.SHARED_DIR.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(bp)
    return app
