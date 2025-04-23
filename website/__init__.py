from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, WorkoutPreferences, WorkoutSplit, WorkoutDay, ExerciseRole, Exercise, SavedPlan
    
    with app.app_context():
        db.create_all()
        

    login_manager = LoginManager()
    # where we send user if no user logged in
    login_manager.login_view = 'auth.login' 
    login_manager.init_app(app)

    # find user by primary key (id)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
