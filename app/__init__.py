from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_sqlalchemy import SQLAlchemy  # İleride kullanılacak

# db = SQLAlchemy()  # İleride kullanılacak

db = SQLAlchemy()

def create_app():
    """
    Flask uygulamasını başlatan ve blueprint'leri kaydeden fabrika fonksiyonu.
    """
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    db.init_app(app)

    # Blueprint'leri import ve register et
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # User modelini import et (migrate için)
    from app.models.user import User

    return app 