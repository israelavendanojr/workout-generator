from website.models.saved_models import SavedPlan, SavedDay, SavedExercise
from flask_login import current_user

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