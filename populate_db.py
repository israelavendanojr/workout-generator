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

    # add equipment

    barbell = Equipment(name="Barbell")
    dumbbell = Equipment(name="Dumbbell")
    machine = Equipment(name="Machine")
    cable = Equipment(name="Cable")
    bodyweight = Equipment(name="Bodyweight")

    db.session.add_all([barbell, dumbbell, machine, cable, bodyweight])
    db.session.commit()

    # add exercises

    # Horizontal Incline Push
    incline_barbell_bench_press = Exercise(name="Incline Barbell Bench Press", role=horizontal_incline_push)
    incline_dumbbell_press = Exercise(name="Incline Dumbbell Press", role=horizontal_incline_push)
    incline_machine_press = Exercise(name="Incline Machine Press", role=horizontal_incline_push)
    decline_push_ups = Exercise(name="Decline Push-Ups", role=horizontal_push)

    # Horizontal Push
    flat_barbell_bench_press = Exercise(name="Flat Barbell Bench Press", role=horizontal_push)
    flat_dumbbell_press = Exercise(name="Flat Dumbbell Press", role=horizontal_push)
    machine_chest_press = Exercise(name="Machine Chest Press", role=horizontal_push)
    push_ups = Exercise(name="Push-Ups", role=horizontal_push)

    # Vertical Push
    overhead_barbell_press = Exercise(name="Overhead Barbell Press", role=vertical_push)
    seated_dumbbell_shoulder_press = Exercise(name="Seated Dumbbell Shoulder Press", role=vertical_push)
    machine_shoulder_press = Exercise(name="Machine Shoulder Press", role=vertical_push)

    # Side Delt Isolation
    dumbbell_lateral_raise = Exercise(name="Dumbbell Lateral Raise", role=side_delt_isolation)
    cable_lateral_raise = Exercise(name="Cable Lateral Raise", role=side_delt_isolation)
    machine_lateral_raise = Exercise(name="Machine Lateral Raise", role=side_delt_isolation)

    # Tricep Isolation
    cable_tricep_pushdown = Exercise(name="Cable Tricep Pushdown", role=tricep_isolation)
    skull_crushers = Exercise(name="Skull Crushers", role=tricep_isolation)

    # Horizontal Pull
    barbell_row = Exercise(name="Barbell Row", role=horizontal_pull)
    dumbbell_row = Exercise(name="Dumbbell Row", role=horizontal_pull)
    machine_row = Exercise(name="Machine Row", role=horizontal_pull)

    # Vertical Pull
    pull_ups = Exercise(name="Pull Ups", role=vertical_pull)
    lat_pulldown = Exercise(name="Lat Pulldown", role=vertical_pull)

    # Rear Delt Isolation
    reverse_pec_deck_fly = Exercise(name="Reverse Pec Deck Fly", role=rear_delt_isolation)
    cable_rear_delt_fly = Exercise(name="Cable Rear Delt Fly", role=rear_delt_isolation)
    dumbbell_rear_delt_fly = Exercise(name="Dumbbell Rear Delt Fly", role=rear_delt_isolation)

    # Bicep Isolation
    dumbbell_incline_curl = Exercise(name="Dumbbell Incline Curl", role=bicep_isolation)
    barbell_curl = Exercise(name="Barbell Curl", role=bicep_isolation)
    preacher_curl = Exercise(name="Preacher Curl", role=bicep_isolation)

    # Lat Isolation
    straight_arm_lat_pulldown = Exercise(name="Straight Arm Lat Pulldown", role=lat_isolation)
    machine_lat_pullover = Exercise(name="Machine Lat Pullover", role=lat_isolation)

    # Squat
    barbell_squat = Exercise(name="Barbell Squat", role=squat)
    hack_squat = Exercise(name="Hack Squat", role=squat)
    leg_press = Exercise(name="Leg Press", role=squat)

    # Hinge
    barbell_deadlift = Exercise(name="Barbell Deadlift", role=hinge)
    barbell_romanian_deadlift = Exercise(name="Barbell Romanian Deadlift", role=hinge)
    machine_hip_thrust = Exercise(name="Machine Hip Thrust", role=hinge)
    back_extension = Exercise(name="Back Extension", role=hinge)

    # Quad Isolation
    leg_extensions = Exercise(name="Leg Extensions", role=quad_isolation)
    sissy_squats = Exercise(name="Sissy Squats", role=quad_isolation)
    adduction_machine = Exercise(name="Adduction Machine", role=quad_isolation)

    # Hamstring Isolation
    lying_hamstring_curl = Exercise(name="Lying Hamstring Curl", role=hamstring_isolation)
    seated_hamstring_curl = Exercise(name="Seated Hamstring Curl", role=hamstring_isolation)

    # Calf Isolation
    standing_calf_raise = Exercise(name="Standing Calf Raise", role=calf_isolation)
    seated_calf_raise = Exercise(name="Seated Calf Raise", role=calf_isolation)

    # Add all exercises to the database
    db.session.add_all([
        # Horizontal Incline Push
        incline_barbell_bench_press,
        incline_dumbbell_press,
        incline_machine_press,
        decline_push_ups,

        # Horizontal Push
        flat_barbell_bench_press,
        flat_dumbbell_press,
        machine_chest_press,
        push_ups,

        # Vertical Push
        overhead_barbell_press,
        seated_dumbbell_shoulder_press,
        machine_shoulder_press,

        # Side Delt Isolation
        dumbbell_lateral_raise,
        cable_lateral_raise,
        machine_lateral_raise,

        # Tricep Isolation
        cable_tricep_pushdown,
        skull_crushers,

        # Horizontal Pull
        barbell_row,
        dumbbell_row,
        machine_row,

        # Vertical Pull
        pull_ups,
        lat_pulldown,

        # Rear Delt Isolation
        reverse_pec_deck_fly,
        cable_rear_delt_fly,
        dumbbell_rear_delt_fly,

        # Bicep Isolation
        dumbbell_incline_curl,
        barbell_curl,
        preacher_curl,

        # Lat Isolation
        straight_arm_lat_pulldown,
        machine_lat_pullover,

        # Squat
        barbell_squat,
        hack_squat,
        leg_press,

        # Hinge
        barbell_deadlift,
        barbell_romanian_deadlift,
        machine_hip_thrust,
        back_extension,

        # Quad Isolation
        leg_extensions,
        sissy_squats,
        adduction_machine,

        # Hamstring Isolation
        lying_hamstring_curl,
        seated_hamstring_curl,

        # Calf Isolation
        standing_calf_raise,
        seated_calf_raise
    ])

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        clear()
        populate()
        print("\nDATABASE POPULATED\n")
