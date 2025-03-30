from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# User login details
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# User selected workout preferences to generate plan from
class WorkoutPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    weekly_days = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.String(100), nullable=False)
    equipment = db.Column(db.Text, nullable=False)

# Workout splits, i.e. PPL, Upper/Lower, etc
class WorkoutSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days_per_week = db.Column(db.Integer, nullable=False)

    # Create many-to-many relationship to WorkoutDay via split_day_association
    workout_days = db.relationship(
        'WorkoutDay', 
        secondary='split_day_association', 
        backref=db.backref('workout_splits_association', lazy='dynamic'),  # Use a unique name here
    )

# Holds structure of given workout day, e.g. Push, Pull, and Leg days in PPL
# WorkoutDay model
class WorkoutDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Many-to-many relationship with ExerciseRole
    exercises = db.relationship(
        'ExerciseRole', 
        secondary='day_role_association', 
        backref='workout_day'
    )

    # Many-to-many relationship with WorkoutSplit, using the split_day_association
    workout_splits = db.relationship(
        'WorkoutSplit', 
        secondary='split_day_association', 
        backref=db.backref('workout_days_association', lazy='dynamic'), 
    )

# Association table for many-to-many relationship, can associate same WorkoutDay to multiples WorkoutSplits
split_day_association = db.Table('split_day_association',
    db.Column('workout_split_id', db.Integer, db.ForeignKey('workout_split.id'), primary_key=True),
    db.Column('workout_day_id', db.Integer, db.ForeignKey('workout_day.id'), primary_key=True)
)

# Defines function of an exercise, e.g. horizontal push, vertical pull, curl, eyc
class ExerciseRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), unique=True, nullable=False)

# Association table for many-to-many relationship, can associate same ExerciseRole to multiple WorkoutDays
day_role_association = db.Table('day_role_association',
    db.Column('workout_day_id', db.Integer, db.ForeignKey('workout_day.id'), primary_key=True),
    db.Column('exercise_role_id', db.Integer, db.ForeignKey('exercise_role.id'), primary_key=True)
)

# Stores exercise information
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('exercise_role.id'), nullable=False)

    # Relationship to link exercises to roles
    role = db.relationship('ExerciseRole', backref='exercises')