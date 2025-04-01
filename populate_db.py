from website import create_app, db
from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association, Equipment, exercise_equipment_association

app = create_app()

# clears database
def clear():
    # Delete associations to prevent foreign key errors
    db.session.query(day_role_association).delete()
    db.session.query(split_day_association).delete()

    # Then delete the main tables
    db.session.query(WorkoutSplit).delete()
    db.session.query(WorkoutDay).delete()
    db.session.query(ExerciseRole).delete()

    # Commit changes to the database
    db.session.commit()

# adds WorkoutSplit and stores in order of insertion
def add_split(name, days_per_week, workout_days):
    split = WorkoutSplit(name=name, days_per_week=days_per_week)
    db.session.add(split)
    db.session.commit()  # Commit to get split.id

    # Insert ordered workout days into association table
    for index, day in enumerate(workout_days):
        db.session.execute(split_day_association.insert().values(
            workout_split_id=split.id,
            workout_day_id=day.id,
            order=index
        ))
    
    db.session.commit()

# associate exercise roles with workout day
def add_structure_to_day(workout_day, exercises):
    # Add exerciseRoles to the day with the correct order
    for index, exercise in enumerate(exercises):
        db.session.execute(day_role_association.insert().values(
            workout_day_id=workout_day.id,
            exercise_role_id=exercise.id,
            order=index  # Ensures the order is maintained
        ))

    db.session.commit()

def add_equipment_to_exercise(exercise, equipment_list):
    for equipment in equipment_list:
        db.session.execute(exercise_equipment_association.insert().values(
            exercise_id=exercise.id,
            equipment_id=equipment.id
        ))
    db.session.commit()

def populate():
    # Create workout days
    full_A = WorkoutDay(name="Full Body A")
    full_B = WorkoutDay(name="Full Body B")
    full_C = WorkoutDay(name="Full Body C")

    upper_A = WorkoutDay(name="Upper A")
    lower_A = WorkoutDay(name="Lower A")
    upper_B = WorkoutDay(name="Upper B")
    lower_B = WorkoutDay(name="Lower B")

    push_A = WorkoutDay(name="Push A")
    pull_A = WorkoutDay(name="Pull A")
    legs_A = WorkoutDay(name="Legs A")
    push_B = WorkoutDay(name="Push B")
    pull_B = WorkoutDay(name="Pull B")
    legs_B = WorkoutDay(name="Legs B")

    chestback_A = WorkoutDay(name="Chest + Back A")
    arms_A = WorkoutDay(name="Arms A")
    chestback_B = WorkoutDay(name="Chest + Back B")
    arms_B = WorkoutDay(name="Arms B")

    db.session.add_all([full_A, full_B, full_C, 
                        upper_A, lower_A, upper_B, lower_B,
                        push_A, pull_A, legs_A, push_B, pull_B, legs_B,
                        chestback_A, chestback_B, arms_A, arms_B])
    db.session.commit()

    # Add workout splits with correct order
    add_split("Full Body", 1, [full_A])
    add_split("Full Body", 2, [full_A, full_B])
    add_split("Full Body", 3, [full_A, full_B, full_C])
    add_split("Upper Lower + Full Body", 3, [upper_A, lower_A, full_A])
    add_split("Upper Lower", 4, [upper_A, lower_A, upper_B, lower_B])
    add_split("Push Pull Legs + Upper Lower", 5, [push_A, pull_A, legs_A, upper_A, lower_A])
    add_split("Arnold + Upper Lower", 5, [chestback_A, arms_A, legs_A, upper_A, lower_A])
    add_split("Upper Lower + Arms", 5, [upper_A, lower_A, upper_B, lower_B, arms_A])
    add_split("Push Pull Legs", 6, [push_A, pull_A, legs_A, push_B, pull_B, legs_B])
    add_split("Arnold", 6, [chestback_A, arms_A, legs_A, chestback_B, arms_B, legs_B])
    add_split("Push Pull Legs + Arnold", 6, [push_A, pull_A, legs_A, chestback_A, arms_A, legs_B])

    # Add exercise roles
    horizontal_incline_push = ExerciseRole(role="Horizontal Incline Push")
    horizontal_push = ExerciseRole(role="Horizontal Push")
    vertical_push = ExerciseRole(role="Vertical Push")
    side_delt_isolation = ExerciseRole(role="Side Delt Isolation")
    tricep_isolation = ExerciseRole(role="Tricep Isolation")

    horizontal_pull = ExerciseRole(role="Horizontal Pull")
    vertical_pull = ExerciseRole(role="Vertical Pull")
    rear_delt_isolation = ExerciseRole(role="Rear Delt Isolation")
    bicep_isolation = ExerciseRole(role="Bicep Isolation")
    lat_isolation = ExerciseRole(role="Lat Isolation")

    squat = ExerciseRole(role="Squat")
    hinge = ExerciseRole(role="Hinge")
    quad_isolation = ExerciseRole(role="Quad Isolation")
    hamstring_isolation = ExerciseRole(role="Hamstring Isolation")
    calf_isolation = ExerciseRole(role="Calf Isolation")

    db.session.add_all([
        horizontal_incline_push, horizontal_push, vertical_push, side_delt_isolation, tricep_isolation, 
        horizontal_pull, vertical_pull, rear_delt_isolation, bicep_isolation, lat_isolation, 
        squat, hinge, quad_isolation, hamstring_isolation, calf_isolation
    ])
    db.session.commit()  # Ensure IDs are assigned

    # Add structure to each workout with correct order
    add_structure_to_day(push_A, [
        horizontal_incline_push, 
        horizontal_push, 
        vertical_push, 
        side_delt_isolation, 
        tricep_isolation
    ])
    
    add_structure_to_day(pull_A, [
        vertical_pull, 
        horizontal_pull, 
        lat_isolation, 
        rear_delt_isolation, 
        bicep_isolation
    ])
    
    add_structure_to_day(legs_A, [
        squat, 
        hinge, 
        quad_isolation, 
        hamstring_isolation, 
        calf_isolation
    ])
    
    add_structure_to_day(push_B, [
        vertical_push, 
        side_delt_isolation, 
        horizontal_incline_push, 
        horizontal_push, 
        tricep_isolation
    ])
    
    add_structure_to_day(pull_B, [
        vertical_pull, 
        horizontal_pull, 
        lat_isolation, 
        rear_delt_isolation, 
        bicep_isolation
    ])
    
    add_structure_to_day(legs_B, [
        squat, 
        hinge, 
        quad_isolation, 
        hamstring_isolation, 
        calf_isolation
    ])

    add_structure_to_day(upper_A, [
        horizontal_incline_push, 
        vertical_pull, 
        horizontal_push, 
        horizontal_pull, 
        side_delt_isolation, 
        bicep_isolation, 
        tricep_isolation
    ])
    
    add_structure_to_day(lower_A, [
        squat, 
        hinge, 
        quad_isolation, 
        hamstring_isolation, 
        calf_isolation
    ])
    
    add_structure_to_day(upper_B, [
        horizontal_incline_push, 
        vertical_pull, 
        horizontal_push, 
        horizontal_pull, 
        rear_delt_isolation, 
        bicep_isolation, 
        tricep_isolation
    ])
    
    add_structure_to_day(lower_B, [
        squat, 
        hinge, 
        quad_isolation, 
        hamstring_isolation, 
        calf_isolation
    ])

    add_structure_to_day(chestback_A, [
        horizontal_incline_push, 
        horizontal_pull, 
        horizontal_push, 
        vertical_pull, 
    ])

    add_structure_to_day(arms_A, [
        vertical_push, 
        side_delt_isolation, 
        rear_delt_isolation, 
        bicep_isolation,
        tricep_isolation 
    ])

    add_structure_to_day(chestback_B, [
        vertical_pull, 
        horizontal_incline_push, 
        horizontal_pull, 
        horizontal_push, 
    ])

    add_structure_to_day(arms_B, [
        vertical_push, 
        side_delt_isolation, 
        rear_delt_isolation, 
        bicep_isolation,
        tricep_isolation 
    ])

    # # add equipment
    # barbell = Equipment(name="Barbell")
    # dumbbell = Equipment(name="Dumbbell")
    # machine = Equipment(name="Machine")
    # cable = Equipment(name="Cable")
    # bodyweight = Equipment(name="Bodyweight")

    # db.session.add_all([barbell, dumbbell, machine, cable, bodyweight])
    # db.session.commit()

    # Add exercises
    exercises = [
        # Horizontal Incline Push
        Exercise(name="Incline Barbell Bench Press", role=horizontal_incline_push, equipment="Barbell"),
        Exercise(name="Incline Dumbbell Press", role=horizontal_incline_push, equipment="Dumbbell"),
        Exercise(name="Incline Machine Press", role=horizontal_incline_push, equipment="Machine"),
        Exercise(name="Decline Push-Ups", role=horizontal_push, equipment="Bodyweight"),

        # Horizontal Push
        Exercise(name="Flat Barbell Bench Press", role=horizontal_push, equipment="Barbell"),
        Exercise(name="Flat Dumbbell Press", role=horizontal_push, equipment="Dumbbell"),
        Exercise(name="Machine Chest Press", role=horizontal_push, equipment="Machine"),
        Exercise(name="Push-Ups", role=horizontal_push, equipment="Bodyweight"),

        # Vertical Push
        Exercise(name="Overhead Barbell Press", role=vertical_push, equipment="Barbell"),
        Exercise(name="Seated Dumbbell Shoulder Press", role=vertical_push, equipment="Dumbbell"),
        Exercise(name="Machine Shoulder Press", role=vertical_push, equipment="Machine"),

        # Side Delt Isolation
        Exercise(name="Dumbbell Lateral Raise", role=side_delt_isolation, equipment="Dumbbell"),
        Exercise(name="Cable Lateral Raise", role=side_delt_isolation, equipment="Cable"),
        Exercise(name="Machine Lateral Raise", role=side_delt_isolation, equipment="Machine"),

        # Tricep Isolation
        Exercise(name="Cable Tricep Pushdown", role=tricep_isolation, equipment="Cable"),
        Exercise(name="Skull Crushers", role=tricep_isolation, equipment="Barbell"),

        # Horizontal Pull
        Exercise(name="Barbell Row", role=horizontal_pull, equipment="Barbell"),
        Exercise(name="Dumbbell Row", role=horizontal_pull, equipment="Dumbbell"),
        Exercise(name="Machine Row", role=horizontal_pull, equipment="Machine"),

        # Vertical Pull
        Exercise(name="Pull Ups", role=vertical_pull, equipment="Bodyweight"),
        Exercise(name="Lat Pulldown", role=vertical_pull, equipment="Cable"),

        # Rear Delt Isolation
        Exercise(name="Reverse Pec Deck Fly", role=rear_delt_isolation, equipment="Machine"),
        Exercise(name="Cable Rear Delt Fly", role=rear_delt_isolation, equipment="Cable"),
        Exercise(name="Dumbbell Rear Delt Fly", role=rear_delt_isolation, equipment="Dumbbell"),

        # Bicep Isolation
        Exercise(name="Dumbbell Incline Curl", role=bicep_isolation, equipment="Dumbbell"),
        Exercise(name="Barbell Curl", role=bicep_isolation, equipment="Barbell"),
        Exercise(name="Preacher Curl", role=bicep_isolation, equipment="Machine"),

        # Lat Isolation
        Exercise(name="Straight Arm Lat Pulldown", role=lat_isolation, equipment="Cable"),
        Exercise(name="Machine Lat Pullover", role=lat_isolation, equipment="Machine"),

        # Squat
        Exercise(name="Barbell Squat", role=squat, equipment="Barbell"),
        Exercise(name="Hack Squat", role=squat, equipment="Machine"),
        Exercise(name="Leg Press", role=squat, equipment="Machine"),

        # Hinge
        Exercise(name="Barbell Deadlift", role=hinge, equipment="Barbell"),
        Exercise(name="Barbell Romanian Deadlift", role=hinge, equipment="Barbell"),
        Exercise(name="Machine Hip Thrust", role=hinge, equipment="Machine"),
        Exercise(name="Back Extension", role=hinge, equipment="Bodyweight"),

        # Quad Isolation
        Exercise(name="Leg Extensions", role=quad_isolation, equipment="Machine"),
        Exercise(name="Sissy Squats", role=quad_isolation, equipment="Bodyweight"),
        Exercise(name="Adduction Machine", role=quad_isolation, equipment="Machine"),

        # Hamstring Isolation
        Exercise(name="Lying Hamstring Curl", role=hamstring_isolation, equipment="Machine"),
        Exercise(name="Seated Hamstring Curl", role=hamstring_isolation, equipment="Machine"),

        # Calf Isolation
        Exercise(name="Standing Calf Raise", role=calf_isolation, equipment="Machine"),
        Exercise(name="Seated Calf Raise", role=calf_isolation, equipment="Machine")
    ]

    # Add all exercises to the database
    db.session.add_all(exercises)



if __name__ == "__main__":
    with app.app_context():
        clear()
        populate()
        print("\nDATABASE POPULATED\n")
