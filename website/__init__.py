from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjdaksdhjkasdhjklasdhjka'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Note
    with app.app_context():
        db.create_all()

    return app

# no longer neccesary? app.app_context() updated solution
# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all()
#         print('Created database')
#     else:
#         print('Database already exist, did not create database')