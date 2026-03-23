from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.extensions import db, jwt, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.dataset_routes import datasets_bp
    from backend.routes.fetch_routes import fetch_bp
    from backend.routes.graph_routes import graph_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(fetch_bp)
    app.register_blueprint(graph_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
