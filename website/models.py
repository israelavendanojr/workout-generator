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
    password = db.Column(db.String(999))

    saved_plans = db.relationship('SavedPlan', backref='owner', lazy=True)

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

# Muscle groups, e.g. chest, shoulders, etc
class MuscleGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Defines function of an exercise, e.g. horizontal push, vertical pull, curl, eyc
class ExerciseRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Association table for many-to-many relationship, can associate same ExerciseRole to multiple WorkoutDays
day_role_association = db.Table('day_role_association',
    db.Column('workout_day_id', db.Integer, db.ForeignKey('workout_day.id'), primary_key=True),
    db.Column('exercise_role_id', db.Integer, db.ForeignKey('exercise_role.id', ondelete='CASCADE'), primary_key=True),
    db.Column('order', db.Integer, nullable=False) 
)

# Type of exercise, e.g. compound, isolation
class ExerciseType(enum.Enum):
    COMPOUND = "Compound"
    ISOLATION = "Isolation"

# Equipment model
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


# Association tables to define many-to-many relationships
primary_muscle_association = db.Table(
    'primary_muscle_association',
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'), primary_key=True),
    db.Column('muscle_group_id', db.Integer, db.ForeignKey('muscle_group.id'), primary_key=True)
)

secondary_muscle_association = db.Table(
    'secondary_muscle_association',
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'), primary_key=True),
    db.Column('muscle_group_id', db.Integer, db.ForeignKey('muscle_group.id'), primary_key=True)
)

# Stores exercise information
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('exercise_role.id'), nullable=False) 
    role = db.relationship('ExerciseRole', backref='exercises')
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    # Relationship to the Equipment model
    equipment = db.relationship('Equipment', backref='exercises')
    type = db.Column(Enum(ExerciseType, name="exercise_type_enum"), nullable=False)
    
    # Relationships for muscles
    primary_muscles = db.relationship(
        'MuscleGroup',
        secondary=primary_muscle_association,
        backref=db.backref('primary_exercises', lazy='dynamic')
    )
    secondary_muscles = db.relationship(
        'MuscleGroup',
        secondary=secondary_muscle_association,
        backref=db.backref('secondary_exercises', lazy='dynamic')
    )

# Saved workout plan attached to user
class SavedPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    split_name = db.Column(db.String(100), nullable=False)
    # stored as json 
    plan = db.Column(db.Text, unique=True, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    days = db.relationship('SavedDay', backref='saved_plan', cascade="all, delete-orphan")


    def __init__(self, split_name, plan_data, user_id):
        self.split_name = split_name
        self.plan = json.dumps(plan_data)  # Convert dict to JSON string
        self.user_id = user_id

    def get_plan_data(self):
            """Ensure the stored plan is returned as a dictionary"""
            try:
                return json.loads(self.plan)  # Convert JSON string back to dict
            except json.JSONDecodeError as e:
                return {} 
            

class SavedDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saved_plan_id = db.Column(db.Integer, db.ForeignKey('saved_plan.id'), nullable=False)
    day_name = db.Column(db.String(100), nullable=False)

    exercises = db.relationship('PlanExercise', backref='workout_day', cascade="all, delete-orphan")

class SavedExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saved_day_id = db.Column(db.Integer, db.ForeignKey('saved_day.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    start_reps = db.Column(db.Integer, nullable=False)
    end_reps = db.Column(db.Integer, nullable=False)
    to_failure = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False)

    exercise = db.relationship('Exercise')
