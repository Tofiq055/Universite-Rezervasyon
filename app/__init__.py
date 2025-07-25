from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.student import student_bp
    app.register_blueprint(student_bp)
    from app.routes.teacher import teacher_bp
    app.register_blueprint(teacher_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    from app.models import User, Device, Category, Reservation

    return app 