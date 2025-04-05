from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Enum
import json
import enum

    
# User login details
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    plans = db.relationship('SavedPlan', backref='owner', lazy=True)

# User selected workout preferences to generate plan from
class WorkoutPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    weekly_days = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.String(100), nullable=False)
    equipment = db.Column(db.Text, nullable=False)

# Association table for many-to-many relationship, can associate same WorkoutDay to multiples WorkoutSplits
split_day_association = db.Table('split_day_association',
    db.Column('workout_split_id', db.Integer, db.ForeignKey('workout_split.id'), primary_key=True),
    db.Column('workout_day_id', db.Integer, db.ForeignKey('workout_day.id'), primary_key=True),
    db.Column('order', db.Integer, nullable=False) 
)

# Workout splits, i.e. PPL, Upper/Lower, etc
class WorkoutSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days_per_week = db.Column(db.Integer, nullable=False)

    # Ordered Many-to-Many Relationship with WorkoutDay
    workout_days = db.relationship(
        'WorkoutDay',
        secondary=split_day_association,
        order_by=split_day_association.c.order, 
        back_populates='workout_splits',
        overlaps="workout_days_association"
    )

class WorkoutDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Many-to-many relationship with ExerciseRole
    structure = db.relationship(
        'ExerciseRole', 
        secondary='day_role_association', 
        backref='workout_days'
    )

    # Many-to-Many Relationship with WorkoutSplit
    workout_splits = db.relationship(
        'WorkoutSplit', 
        secondary=split_day_association, 
        back_populates='workout_days',
        overlaps="workout_splits_association"
    )

# Defines function of an exercise, e.g. horizontal push, vertical pull, curl, eyc
class ExerciseRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), unique=True, nullable=False)

# Association table for many-to-many relationship, can associate same ExerciseRole to multiple WorkoutDays
day_role_association = db.Table('day_role_association',
    db.Column('workout_day_id', db.Integer, db.ForeignKey('workout_day.id'), primary_key=True),
    db.Column('exercise_role_id', db.Integer, db.ForeignKey('exercise_role.id'), primary_key=True),
    db.Column('order', db.Integer, nullable=False) 
)

# exercise_equipment_association = db.Table(
#     'exercise_equipment_association',
#     db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'), primary_key=True),
#     db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
# )

class ExerciseType(enum.Enum):
    COMPOUND = "Compound"
    ISOLATION = "Isolation"

# Stores exercise information
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('exercise_role.id'), nullable=False) 
    role = db.relationship('ExerciseRole', backref='exercises')
    equipment = db.Column(db.String(100), nullable=False)
    type = db.Column(Enum(ExerciseType), nullable=False)

    # Many-to-Many relationship with Equipment
    # equipment = db.relationship('Equipment', secondary='exercise_equipment_association', back_populates='exercises')

# class Equipment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), unique=True, nullable=False)

#     # Relationship to Exercise
#     exercises = db.relationship('Exercise', secondary='exercise_equipment_association', back_populates='equipment')

# Saved workout plan attached to user
class SavedPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    split_name = db.Column(db.String(100), nullable=False)
    # stored as json 
    plan = db.Column(db.Text, unique=True, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, split_name, plan_data, user_id):
        self.split_name = split_name
        self.plan = json.dumps(plan_data)  # Convert dict to JSON string
        self.user_id = user_id

    def get_plan_data(self):
            """Ensure the stored plan is returned as a dictionary"""
            try:
                print("Encoded JSON:")
                return json.loads(self.plan)  # Convert JSON string back to dict
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return {} 