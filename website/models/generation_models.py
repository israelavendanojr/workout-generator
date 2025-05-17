from website import db
from sqlalchemy import Enum
import enum

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
