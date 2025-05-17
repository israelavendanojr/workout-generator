from website import db
from website.models.generation_models import Exercise

def get_priority_mapping():
    """Return the mapping of muscle groups to specific muscles."""
    return {
        "Shoulders": {"Side Delts", "Front Delts", "Rear Delts"},
        "Back": {"Upper Back", "Lower Back", "Lats", "Traps"},
        "Chest": {"Upper Chest", "Lower Chest"},
        "Biceps": {"Biceps"},
        "Triceps": {"Triceps"},
        "Quads": {"Quads"},
        "Hamstrings": {"Hamstrings"},
        "Glutes": {"Glutes"},
        "Calves": {"Calves"}
    }

def get_muscle_group(exercise):
    """Return the muscle group the exercise belongs to."""
    # Get the actual exercise object from the database
    exercise_obj = Exercise.query.get(exercise["exercise_id"])
    if not exercise_obj:
        return "Other"

    priority_mapping = get_priority_mapping()
    for group, muscles in priority_mapping.items():
        if any(muscle.name in muscles for muscle in exercise_obj.primary_muscles):
            return group
    return "Other"  # Default to "Other" if no match is found

def has_muscle_priority(priority_muscles, exercise_id):
    """Check if the exercise has a muscle priority."""
    exercise_obj = Exercise.query.get(exercise_id)
    if not exercise_obj:
        return False

    # Check if any of the muscles in the priority mapping are in the primary_muscles set
    priority_mapping = get_priority_mapping()
    for priority in priority_muscles:
        specific_muscles = priority_mapping.get(priority, {priority})
        if any(muscle.name in specific_muscles for muscle in exercise_obj.primary_muscles):
            return True
    return False

def has_muscle_interference(exercise_1_id, exercise_2_id):
    """Check if two exercises have muscle interference."""
    exercise_1 = Exercise.query.get(exercise_1_id)
    exercise_2 = Exercise.query.get(exercise_2_id)
    
    if not exercise_1 or not exercise_2:
        return False

    muscles_1 = {muscle.name for muscle in exercise_1.primary_muscles} | {muscle.name for muscle in exercise_1.secondary_muscles}
    muscles_2 = {muscle.name for muscle in exercise_2.primary_muscles} | {muscle.name for muscle in exercise_2.secondary_muscles}

    if muscles_1 & muscles_2:  # If there's any overlap in the muscles, it's an interference
        return True
    return False