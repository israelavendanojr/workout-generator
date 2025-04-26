from website import db
from website.models import WorkoutSplit, WorkoutDay, Exercise, ExerciseRole, ExerciseType, Equipment, day_role_association
from collections import defaultdict
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

def get_suitable_exercises(role, equipment):
    """Get exercises that match the role and available equipment."""
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
    primary_muscles = [muscle.name for muscle in exercise.primary_muscles]
    secondary_muscles = [muscle.name for muscle in exercise.secondary_muscles]
    
    return {
        "name": exercise.name,
        "sets": sets,
        "start_reps": start_reps,
        "end_reps": end_reps,
        "role": {
            "id": role.id,
            "name": role.name
        },
        "id": exercise.id,
        "toFailure": to_failure,
        "primary_muscles": primary_muscles,
        "secondary_muscles": secondary_muscles
    }

def create_null_exercise_info(role):
    """Create null exercise information when no suitable exercise is found."""
    return {
        "name": f"No suitable exercise for {role.name} found",
        "sets": 0,
        "start_reps": 0,
        "end_reps": 0,
        "role": None,
        "toFailure": None,
        "exercise_obj": None,
        "primary_muscles": None,
        "secondary_muscles": None
    }

def generate_day_plan(day, equipment, approach, bodyweight_exercises, priority_muscles):
    """Generate plan for a single workout day."""
    day_info = {
        "name": day.name,
        "exercises": []
    }

    ordered_roles = get_ordered_roles(day)
    
    # Add bodyweight to equipment if specified
    if bodyweight_exercises != "Absent":
        equipment = equipment + ["Bodyweight"]

    # Generate exercises for each role
    for role in ordered_roles:
        exercises = get_suitable_exercises(role, equipment)
        
        if exercises:
            random_exercise = random.choice(exercises)
            sets, start_reps, end_reps = determine_sets_and_reps(random_exercise, approach)
            
            # Handle bodyweight progression
            to_failure = (random_exercise.equipment == "Bodyweight" and 
                         bodyweight_exercises == "Bodyweight")
            
            exercise_info = create_exercise_info(random_exercise, role, sets, start_reps, end_reps, to_failure)
        else:
            exercise_info = create_null_exercise_info(role)
            
        day_info["exercises"].append(exercise_info)

    # Reorder exercises by priority, bottle neck exercises up if they are given specified priority
    for i in range(len(day_info["exercises"])):
        exercise_info = day_info["exercises"][i]
        # previous_exercise_info = day_info["exercises"][i-1]
        # hasPriority = False
        
        print(exercise_info["name"], exercise_info["primary_muscles"], exercise_info["secondary_muscles"])

    print(day_info)
    print("--------------------------------")

    



    
    return day_info

def has_muscle_priority(priority_muscles, primary_muscles, secondary_muscles):
    """Check if the exercise has a muscle priority."""
    priority_mapping = {
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

    # combine primary and secondary muscles 
    all_muscles = set(primary_muscles) | set(secondary_muscles)
    
    # check if any of the muscles in the priority mapping are in the all_muscles set
    for priority in priority_muscles:
        specific_muscles = priority_mapping.get(priority, {priority})
        if specific_muscles & all_muscles:
            return True
    return False

def generate_plans(days_available, equipment, approach, see_plans, bodyweight_exercises, priority_muscles):
    """Generate workout plans based on user preferences."""
    workout_plans = []
    workout_splits = get_workout_splits(days_available)
    print("PRIORITY MUSCLES", priority_muscles, "\n")
    
    for split in workout_splits:
        plan = {
            "split_name": split.name,
            "days": []
        }
        
        for day in split.workout_days:
            day_info = generate_day_plan(day, equipment, approach, bodyweight_exercises, priority_muscles)
            plan["days"].append(day_info)
        
        workout_plans.append(plan)
        
        if see_plans == "No":
            break
    
    return workout_plans 