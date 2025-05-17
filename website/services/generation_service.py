from website import db
from website.utils.exercise_utils import (
    get_suitable_exercises,
    determine_sets_and_reps,
    create_exercise_info,
    create_null_exercise_info
)
from website.utils.generation_utils import (
    get_workout_splits,
    get_ordered_roles,
    reorder_exercises_with_priority
)

def generate_plans(days_available, equipment, approach, see_plans, bodyweight_exercises, priority_muscles, isolation_first):
    """Generate workout plans based on user preferences."""
    workout_plans = []
    workout_splits = get_workout_splits(days_available)
    
    for split in workout_splits:
        plan = {
            "split_name": split.name,
            "days": []
        }
        
        for day in split.workout_days:
            day_info = generate_day_plan(day, equipment, approach, bodyweight_exercises, priority_muscles, isolation_first)
            plan["days"].append(day_info)
        
        workout_plans.append(plan)
        
        if see_plans == "No":
            break
    
    return workout_plans

def generate_day_plan(day, equipment, approach, bodyweight_exercises, priority_muscles, isolation_first):
    """Generate plan for a single workout day."""
    day_info = {
        "name": day.name,
        "exercises": []
    }

    # Add bodyweight to equipment if specified
    if bodyweight_exercises != "Absent":
        equipment = equipment + ["Bodyweight"]

    # Generate exercises for the day
    day_info["exercises"] = generate_exercises_for_day(day, equipment, approach, bodyweight_exercises)

    muscle_exceptions = ["Rear Delts", "Front Delts"]
    reorder_exercises_with_priority(day_info, priority_muscles, muscle_exceptions, isolation_first)
    
    return day_info

def generate_exercises_for_day(day, equipment, approach, bodyweight_exercises):
    """Generate exercises for each role in the day plan."""
    exercises_for_day = []
    ordered_roles = get_ordered_roles(day)

    for role in ordered_roles:
        exercises = get_suitable_exercises(role, equipment)
        
        if exercises:
            import random
            random_exercise = random.choice(exercises)
            sets, start_reps, end_reps = determine_sets_and_reps(random_exercise, approach)
            
            # Handle bodyweight progression
            to_failure = False
            if hasattr(random_exercise, 'equipment') and random_exercise.equipment == "Bodyweight" and bodyweight_exercises == "Bodyweight":
                to_failure = True
            
            exercise_info = create_exercise_info(random_exercise, role, sets, start_reps, end_reps, to_failure)
        else:
            exercise_info = create_null_exercise_info(role)
        
        exercises_for_day.append(exercise_info)
    
    return exercises_for_day