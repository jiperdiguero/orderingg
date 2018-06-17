from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from app.routes import rest

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(rest)

    return app
