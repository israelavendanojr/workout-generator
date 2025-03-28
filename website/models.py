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
    
    # Schedule
    weekly_days = db.Column(db.Integer, nullable=False)
    session_length = db.Column(db.Integer, nullable=False)
    
    # Goals, can later include muscles to prioritze/deprioritze, injuries, and strength metrics
    goal = db.Column(db.String(100), nullable=False)

    # Logistics
    equipment = db.Column(db.Text, nullable=False)

# Workout splits, i.e. PPL, Upper/Lower, etc
class WorkoutSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # create relationship to create plan structure
    workout_days = db.relationship('WorkoutDay', backref='split', cascade="all, delete-orphan")

# Holds structure of given workout day, e.g. Push, Pull, and Leg days in PPL
class WorkoutDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    exercises = db.relationship('ExerciseRole', backref='workout_day', cascade="all, delete-orphan")

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