from website import db

# Saved workout plan attached to user
class SavedPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    split_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    days = db.relationship('SavedDay', backref='saved_plan', cascade="all, delete-orphan")

    def __init__(self, split_name, user_id):
        self.split_name = split_name
        self.user_id = user_id

            
# Saved workout day, contains saved exercise information for a single workout day
class SavedDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saved_plan_id = db.Column(db.Integer, db.ForeignKey('saved_plan.id'), nullable=False)
    day_name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    exercises = db.relationship('SavedExercise', backref='workout_day', cascade="all, delete-orphan")

# Saved exercise, contains saved exercise information for a single exercise
class SavedExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saved_day_id = db.Column(db.Integer, db.ForeignKey('saved_day.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    start_reps = db.Column(db.Integer, nullable=False)
    end_reps = db.Column(db.Integer, nullable=False)
    to_failure = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False)

    exercise = db.relationship('Exercise')
    notes = db.relationship('Note', backref='saved_exercise', cascade="all, delete-orphan")

# Note model for exercise notes
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saved_exercise_id = db.Column(db.Integer, db.ForeignKey('saved_exercise.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    def __init__(self, content, saved_exercise_id, order):
        self.content = content
        self.saved_exercise_id = saved_exercise_id
        self.order = order
