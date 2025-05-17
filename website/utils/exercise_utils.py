from website.models.saved_models import SavedPlan, SavedDay, SavedExercise
from flask_login import current_user
from website import db
from website.models.generation_models import Exercise, ExerciseType
import random

def validate_exercise_swap(exercise_id, plan_id):
    """
    Validate that the exercise being swapped belongs to the specified plan
    and the current user has permission to modify it
    """
    # Find the saved exercise
    saved_exercise = SavedExercise.query.get_or_404(exercise_id)
    
    # Get the day and plan
    saved_day = saved_exercise.workout_day
    saved_plan = saved_day.saved_plan
    
    # Verify the exercise belongs to the plan
    if saved_plan.id != plan_id:
        return False, "Exercise does not belong to this plan"
    
    # Verify the plan belongs to the current user
    if saved_plan.user_id != current_user.id:
        return False, "Unauthorized plan access"
    
    return True, saved_exercise

def get_exercise_by_id(exercise_id):
    """
    Get an exercise by ID
    """
    from website.models.generation_models import Exercise
    return Exercise.query.get_or_404(exercise_id)


# Exercise Generation 

def get_suitable_exercises(role, equipment):
    """Get exercises that match the role and available equipment."""
    from website.models.generation_models import Equipment
    
    exercises = (
        db.session.query(Exercise)
        .join(Exercise.equipment)
        .filter(Equipment.name.in_(equipment))
        .filter(Exercise.role == role)
        .all()
    )
    return exercises

def determine_sets_and_reps(exercise, approach):
    """Determine sets and reps based on exercise type and approach."""
    roll = random.randint(1, 2)
    sets = 0
    start_reps = 0
    end_reps = 0

    if approach == "low_volume":
        if exercise.type == ExerciseType.COMPOUND:
            if roll == 1:
                sets, start_reps, end_reps = 2, 4, 6
            else:
                sets, start_reps, end_reps = 2, 6, 8
        elif exercise.type == ExerciseType.ISOLATION:
            if roll == 1:
                sets, start_reps, end_reps = 2, 6, 8
            else:
                sets, start_reps, end_reps = 1, 8, 10
    elif approach == "moderate_volume":
        if exercise.type == ExerciseType.COMPOUND:
            if roll == 1:
                sets, start_reps, end_reps = 3, 6, 10
            else:
                sets, start_reps, end_reps = 3, 8, 12
        elif exercise.type == ExerciseType.ISOLATION:
            if roll == 1:
                sets, start_reps, end_reps = 2, 8, 10
            else:
                sets, start_reps, end_reps = 3, 8, 12
    elif approach == "high_volume":
        if exercise.type == ExerciseType.COMPOUND:
            if roll == 1:
                sets, start_reps, end_reps = 4, 8, 12
            else:
                sets, start_reps, end_reps = 3, 10, 15
        elif exercise.type == ExerciseType.ISOLATION:
            if roll == 1:
                sets, start_reps, end_reps = 3, 8, 12
            else:
                sets, start_reps, end_reps = 3, 10, 15

    return sets, start_reps, end_reps

def create_exercise_info(exercise, role, sets, start_reps, end_reps, to_failure=False):
    """Create exercise information dictionary."""
    return {
        "exercise_id": exercise.id,
        "name": exercise.name,
        "sets": sets,
        "start_reps": start_reps,
        "end_reps": end_reps,
        "to_failure": to_failure,
        "order": 0  # This will be set when saving to the database
    }

def create_null_exercise_info(role):
    """Create null exercise information when no suitable exercise is found."""
    return {
        "exercise_id": None,
        "name": f"No suitable exercise for {role.name} found",
        "sets": 0,
        "start_reps": 0,
        "end_reps": 0,
        "to_failure": False,
        "order": 0
    }