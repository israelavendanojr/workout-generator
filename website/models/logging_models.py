from website import db
from sqlalchemy.sql import func

class WeeklyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    saved_plan_id = db.Column(db.Integer, db.ForeignKey('saved_plan.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', backref='weekly_logs')
    saved_plan = db.relationship('SavedPlan', backref='weekly_logs')

    workout_logs = db.relationship('WorkoutLog', backref='weekly_log', cascade="all, delete-orphan")

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weekly_log_id = db.Column(db.Integer, db.ForeignKey('weekly_log.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    saved_day_id = db.Column(db.Integer, db.ForeignKey('saved_day.id'), nullable=False)
    date = db.Column(db.Date, default=func.current_date(), nullable=False)

    user = db.relationship('User', backref='workout_logs')
    saved_day = db.relationship('SavedDay', backref='workout_logs')

class LoggedExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_log_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'), nullable=False)
    saved_exercise_id = db.Column(db.Integer, db.ForeignKey('saved_exercise.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(300), nullable=True)

    sets = db.relationship('LoggedSet', backref='logged_exercise', cascade="all, delete-orphan")

class LoggedSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logged_exercise_id = db.Column(db.Integer, db.ForeignKey('logged_exercise.id'), nullable=False)

    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rest_time = db.Column(db.Integer, nullable=True)