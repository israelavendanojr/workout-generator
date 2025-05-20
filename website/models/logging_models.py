from website import db
from sqlalchemy.sql import func

class LoggedWeek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    saved_plan_id = db.Column(db.Integer, db.ForeignKey('saved_plan.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', backref='logged_weeks')
    saved_plan = db.relationship('SavedPlan', backref='logged_weeks')
    logged_days = db.relationship('LoggedDay', backref='logged_week', cascade="all, delete-orphan")


class LoggedDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logged_week_id = db.Column(db.Integer, db.ForeignKey('logged_week.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    saved_day_id = db.Column(db.Integer, db.ForeignKey('saved_day.id'), nullable=False)
    date = db.Column(db.Date, default=func.current_date(), nullable=False)

    user = db.relationship('User', backref='logged_days')
    saved_day = db.relationship('SavedDay', backref='logged_days')
    logged_exercises = db.relationship('LoggedExercise', backref='logged_day', cascade="all, delete-orphan")


class LoggedExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logged_day_id = db.Column(db.Integer, db.ForeignKey('logged_day.id'), nullable=False) 
    saved_exercise_id = db.Column(db.Integer, db.ForeignKey('saved_exercise.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(300), nullable=True)

    sets = db.relationship('LoggedSet', backref='logged_exercise', cascade="all, delete-orphan")
    saved_exercise = db.relationship('SavedExercise', backref='logged_exercises')


class LoggedSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logged_exercise_id = db.Column(db.Integer, db.ForeignKey('logged_exercise.id'), nullable=False)  

    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rest_time = db.Column(db.Integer, nullable=True)
