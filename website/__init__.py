from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# csrf = CSRFProtect()

# Set login route
login_manager.login_view = "auth.login"

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Config
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # csrf.init_app(app)
    login_manager.init_app(app)

    # Models (ensures proper relationship loading)
    from website.models.user_model import User
    from website.models.saved_models import SavedPlan, SavedDay, SavedExercise, Note
    from website.models.generation_models import Exercise, ExerciseRole

    # User loader
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Blueprints
    from website.routes.views import views
    from website.routes.plan_routes import plan_routes
    from website.routes.day_routes import day_routes
    from website.routes.exercise_routes import exercise_routes
    from website.auth import auth
    from website.routes.log_routes import log_routes

    app.register_blueprint(views)
    app.register_blueprint(plan_routes)
    app.register_blueprint(day_routes)
    app.register_blueprint(exercise_routes)
    app.register_blueprint(auth)
    app.register_blueprint(log_routes)

    return app
