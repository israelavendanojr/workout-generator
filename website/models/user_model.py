from website import db
from flask_login import UserMixin

# User login details
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(999))

    saved_plans = db.relationship('SavedPlan', backref='owner', lazy=True)
