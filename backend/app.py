import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS
from models import db


def create_app():
    app = Flask(__name__, static_folder=None)
    # basic config via env vars
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )

    # 默认使用 MySQL（生产/开发统一），若要保留 SQLite 请设置 USE_SQLITE=true
    if os.getenv("USE_SQLITE", "false").lower() == "true":
        # prefer existing instance DB if present for local dev
        instance_db = os.path.join(os.getcwd(), "instance", "ml_learner.db")
        if os.path.exists(instance_db):
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{instance_db}"
        else:
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ml_learner.db"
    else:
        # MySQL配置（生产环境使用）
        user = os.getenv("DATABASE_USER", "ml_user")
        password = os.getenv("DATABASE_PASSWORD", "Yjk381088#")
        host = os.getenv("DATABASE_HOST", "127.0.0.1")
        port = os.getenv("DATABASE_PORT", "3306")
        name = os.getenv("DATABASE_NAME", "ml_learner")
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    # logging
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    handler = RotatingFileHandler(
        os.path.join(logs_dir, "app.log"), maxBytes=10 * 1024 * 1024, backupCount=5
    )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # import models to ensure they are registered with SQLAlchemy
    import models  # noqa: F401

    # create tables (best-effort; do not crash server if DB is unreachable)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(
                f"Failed to create tables with configured DB ({e}), "
                "continuing without creating tables so server can start."
            )

    # register blueprints
    from routes.auth import auth_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

    return app


if __name__ == "__main__":
    print("Creating app...")
    app = create_app()
    port = int(os.getenv("PORT", 5001))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
