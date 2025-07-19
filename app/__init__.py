from flask import Flask
# from flask_sqlalchemy import SQLAlchemy  # İleride kullanılacak

# db = SQLAlchemy()  # İleride kullanılacak

def create_app():
    """
    Flask uygulamasını başlatan ve blueprint'leri kaydeden fabrika fonksiyonu.
    """
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    # db.init_app(app)  # İleride kullanılacak

    # Blueprint'leri import ve register et
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app 