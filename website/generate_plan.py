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

def generate_day_plan(day, equipment, approach, bodyweight_exercises, priority_muscles, isolation_first):
    """Generate plan for a single workout day."""
    day_info = {
        "name": day.name,
        "exercises": []
    }

    ordered_roles = get_ordered_roles(day)
    
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
            random_exercise = random.choice(exercises)
            sets, start_reps, end_reps = determine_sets_and_reps(random_exercise, approach)
            
            # Handle bodyweight progression
            to_failure = (random_exercise.equipment == "Bodyweight" and bodyweight_exercises == "Bodyweight")
            
            exercise_info = create_exercise_info(random_exercise, role, sets, start_reps, end_reps, to_failure)
        else:
            exercise_info = create_null_exercise_info(role)
        
        exercises_for_day.append(exercise_info)
    
    return exercises_for_day

def reorder_exercises_with_priority(day_info, priority_muscles, muscle_exceptions=None, isolation_first=False):
    """
    Reorder exercises by priority, moving exercises up if they are given specified priority.
    They will stop moving up when there is muscle interference, unless the exercise is associated with a muscle group in the exceptions list.
    """

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

    if muscle_exceptions is None:
        muscle_exceptions = set()  # No exceptions by default
    
    def get_muscle_group(exercise):
        """Return the muscle group the exercise belongs to."""
        # Get the actual exercise object from the database
        exercise_obj = Exercise.query.get(exercise["exercise_id"])
        if not exercise_obj:
            return "Other"

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
                    if not has_muscle_interference(exercise_info["exercise_id"], prev_exercise_info["exercise_id"]):
                        day_info["exercises"][i], day_info["exercises"][i - 1] = day_info["exercises"][i - 1], day_info["exercises"][i]
                        i -= 1
                    else:
                        break  # Stop moving up if there's interference and the exercise is not in the exception group

            print(f"Moved {exercise_obj.name} to top")

        # Print exercise name and its involved muscles
        print(exercise_obj.name, [m.name for m in exercise_obj.primary_muscles], [m.name for m in exercise_obj.secondary_muscles])

    # Print the final order of exercises after prioritization
    print(day_info)
    print("--------------------------------\n")
        
    return day_info


def generate_plans(days_available, equipment, approach, see_plans, bodyweight_exercises, priority_muscles, isolation_first):
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
            day_info = generate_day_plan(day, equipment, approach, bodyweight_exercises, priority_muscles, isolation_first)
            plan["days"].append(day_info)
        
        workout_plans.append(plan)
        
        if see_plans == "No":
            break
    
    return workout_plans 