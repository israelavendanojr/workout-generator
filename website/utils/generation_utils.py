from website import db
from website.models.generation_models import WorkoutSplit, WorkoutDay, Exercise, ExerciseRole, ExerciseType, Equipment, day_role_association
import random

def get_workout_splits(days_available):
    """Get all workout splits for the given number of days."""
    return WorkoutSplit.query.filter_by(days_per_week=days_available).all()

def get_ordered_roles(day):
    """Get ordered exercise roles for a workout day."""
    return (
        db.session.query(ExerciseRole)
        .join(day_role_association)
        .filter(day_role_association.c.workout_day_id == day.id)
        .order_by(day_role_association.c.order)
        .all()
    )

def reorder_exercises_with_priority(day_info, priority_muscles, muscle_exceptions=None, isolation_first=False):
    """
    Reorder exercises by priority, moving exercises up if they are given specified priority.
    They will stop moving up when there is muscle interference, unless the exercise is associated 
    with a muscle group in the exceptions list.
    """
    from website.utils.muscle_utils import get_priority_mapping, get_muscle_group, has_muscle_priority, has_muscle_interference

    if muscle_exceptions is None:
        muscle_exceptions = set()  # No exceptions by default
    
    for i in range(len(day_info["exercises"])):
        exercise_info = day_info["exercises"][i]
        exercise_obj = Exercise.query.get(exercise_info["exercise_id"])
        
        if not exercise_obj:
            print(f"Warning: Exercise with ID {exercise_info['exercise_id']} not found")
            continue

        has_priority = has_muscle_priority(priority_muscles, exercise_info["exercise_id"])
        current_muscle_group = get_muscle_group(exercise_info)

        # Move exercise up to the top of the list, until there is muscle interference
        if has_priority:
            move_exercise_up(day_info, i, exercise_obj, current_muscle_group, isolation_first)

    return day_info

def move_exercise_up(day_info, i, exercise_obj, current_muscle_group, isolation_first):
    """Helper function to move exercises up in priority list"""
    from website.utils.muscle_utils import get_muscle_group, has_muscle_interference
    
    while i > 0:
        prev_exercise_info = day_info["exercises"][i - 1]
        prev_muscle_group = get_muscle_group(prev_exercise_info)

        # Ensure exercises from the same muscle group do not get reordered
        if current_muscle_group == prev_muscle_group:
            break  # Stop moving up if they belong to the same muscle group

        # If it's a compound exercise or isolation first is true, ignore muscle interference
        if exercise_obj.type == ExerciseType.COMPOUND:
            day_info["exercises"][i], day_info["exercises"][i - 1] = day_info["exercises"][i - 1], day_info["exercises"][i]
            i -= 1
        else:
            if not has_muscle_interference(exercise_obj.id, prev_exercise_info["exercise_id"]):
                day_info["exercises"][i], day_info["exercises"][i - 1] = day_info["exercises"][i - 1], day_info["exercises"][i]
                i -= 1
            else:
                break  # Stop moving up if there's interference and the exercise is not in the exception group