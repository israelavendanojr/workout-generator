from website import create_app, db
from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association, ExerciseType, EquipmentType, MuscleGroup, primary_muscle_association, secondary_muscle_association, Equipment

app = create_app()

# clears database
def clear():
    # Delete associations to prevent foreign key errors
    db.session.query(day_role_association).delete()
    db.session.query(split_day_association).delete()
    db.session.query(primary_muscle_association).delete()
    db.session.query(secondary_muscle_association).delete()

    # Then delete the main tables in the correct order
    db.session.query(Exercise).delete()  # Delete exercises first
    db.session.query(ExerciseRole).delete()  # Then delete exercise roles
    db.session.query(WorkoutSplit).delete()
    db.session.query(WorkoutDay).delete()
    db.session.query(MuscleGroup).delete()

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
    full_A = WorkoutDay(name="Full Body")
    full_B = WorkoutDay(name="Full Body")
    full_C = WorkoutDay(name="Full Body")

    upper_A = WorkoutDay(name="Upper")
    lower_A = WorkoutDay(name="Lower")
    upper_B = WorkoutDay(name="Upper")
    lower_B = WorkoutDay(name="Lower")

    push_A = WorkoutDay(name="Push")
    pull_A = WorkoutDay(name="Pull")
    legs_A = WorkoutDay(name="Legs")
    push_B = WorkoutDay(name="Push")
    pull_B = WorkoutDay(name="Pull")
    legs_B = WorkoutDay(name="Legs")

    chestback_A = WorkoutDay(name="Chest + Back")
    arms_A = WorkoutDay(name="Arms")
    chestback_B = WorkoutDay(name="Chest + Back")
    arms_B = WorkoutDay(name="Arms")

    torso_A = WorkoutDay(name="Torso")
    limb_A = WorkoutDay(name="Limb")
    torso_B = WorkoutDay(name="Torso")
    limb_B = WorkoutDay(name="Limb")

    db.session.add_all([full_A, full_B, full_C, 
                        upper_A, lower_A, upper_B, lower_B,
                        push_A, pull_A, legs_A, push_B, pull_B, legs_B,
                        chestback_A, chestback_B, arms_A, arms_B,
                        torso_A, limb_A, torso_B, limb_B])
    db.session.commit()

    # Add workout splits with correct order
    add_split("Full Body", 1, [full_A])
    add_split("Full Body", 2, [full_A, full_B])
    add_split("Full Body", 3, [full_A, full_B, full_C])
    add_split("Upper Lower + Full Body", 3, [upper_A, lower_A, full_A])
    add_split("Upper Lower", 4, [upper_A, lower_A, upper_B, lower_B])
    add_split("Torso Limb", 4, [torso_A, limb_A, torso_B, limb_B])
    add_split("Push Pull Legs + Upper Lower", 5, [push_A, pull_A, legs_A, upper_A, lower_A])
    add_split("Arnold + Upper Lower", 5, [chestback_A, arms_A, legs_A, upper_A, lower_A])
    add_split("Upper Lower + Arms", 5, [upper_A, lower_A, upper_B, lower_B, arms_A])
    add_split("Push Pull Legs", 6, [push_A, pull_A, legs_A, push_B, pull_B, legs_B])
    add_split("Arnold", 6, [chestback_A, arms_A, legs_A, chestback_B, arms_B, legs_B])
    add_split("Push Pull Legs + Arnold", 6, [push_A, pull_A, legs_A, chestback_A, arms_A, legs_B])

    # Add exercise roles
    horizontal_incline_push = ExerciseRole(name="Horizontal Incline Push")
    horizontal_push = ExerciseRole(name="Horizontal Push")
    vertical_push = ExerciseRole(name="Vertical Push")
    side_delt_isolation = ExerciseRole(name="Side Delt Isolation")
    tricep_isolation = ExerciseRole(name="Tricep Isolation")

    horizontal_pull = ExerciseRole(name="Horizontal Pull")
    vertical_pull = ExerciseRole(name="Vertical Pull")
    rear_delt_isolation = ExerciseRole(name="Rear Delt Isolation")
    bicep_isolation = ExerciseRole(name="Bicep Isolation")
    lat_isolation = ExerciseRole(name="Lat Isolation")

    squat = ExerciseRole(name="Squat")
    hinge = ExerciseRole(name="Hinge")
    quad_isolation = ExerciseRole(name="Quad Isolation")
    hamstring_isolation = ExerciseRole(name="Hamstring Isolation")
    calf_isolation = ExerciseRole(name="Calf Isolation")

    db.session.add_all([
        horizontal_incline_push, horizontal_push, vertical_push, side_delt_isolation, tricep_isolation, 
        horizontal_pull, vertical_pull, rear_delt_isolation, bicep_isolation, lat_isolation, 
        squat, hinge, quad_isolation, hamstring_isolation, calf_isolation
    ])
    db.session.commit()

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

    add_structure_to_day(full_A, [
        horizontal_push,
        vertical_push,
        vertical_pull,
        bicep_isolation,
        tricep_isolation,
        quad_isolation,
        hamstring_isolation,
        calf_isolation
    ])

    add_structure_to_day(full_B, [
        squat,
        hinge,
        horizontal_incline_push,
        horizontal_pull,
        rear_delt_isolation,
        calf_isolation,
        bicep_isolation,
        tricep_isolation
    ])

    add_structure_to_day(full_C, [
        hinge,
        horizontal_incline_push,
        vertical_pull,
        side_delt_isolation,
        squat,
        bicep_isolation,
        tricep_isolation,
        calf_isolation,
    ])

    add_structure_to_day(torso_A, [
        horizontal_incline_push, 
        vertical_pull, 
        horizontal_push, 
        horizontal_pull, 
        side_delt_isolation, 
        rear_delt_isolation
    ])
    
    add_structure_to_day(limb_A, [
        bicep_isolation, 
        tricep_isolation,
        squat, 
        hinge, 
        quad_isolation, 
        hamstring_isolation, 
        calf_isolation
    ])

    add_structure_to_day(torso_B, [
        horizontal_pull, 
        horizontal_incline_push, 
        vertical_pull, 
        horizontal_push, 
        rear_delt_isolation,
        side_delt_isolation 
    ])
    
    add_structure_to_day(limb_B, [
        tricep_isolation,
        bicep_isolation, 
        hinge, 
        squat, 
        hamstring_isolation, 
        quad_isolation, 
        calf_isolation
    ])

    # Add muscle groups
    muscle_groups = [
        # Chest
        MuscleGroup(name="Upper Chest"),
        MuscleGroup(name="Lower Chest"),

        # Back
        MuscleGroup(name="Upper Back"),
        MuscleGroup(name="Lower Back"),
        MuscleGroup(name="Lats"),
        MuscleGroup(name="Traps"),

        # Shoulders
        MuscleGroup(name="Front Delts"),
        MuscleGroup(name="Side Delts"),
        MuscleGroup(name="Rear Delts"),

        # Arms
        MuscleGroup(name="Biceps"),
        MuscleGroup(name="Triceps"),

        # Legs
        MuscleGroup(name="Quads"),
        MuscleGroup(name="Hamstrings"),
        MuscleGroup(name="Glutes"),
        MuscleGroup(name="Calves")
    ]
    db.session.add_all(muscle_groups)
    db.session.commit()

    # Get muscle groups for primary and secondary muscles
    upper_chest = MuscleGroup.query.filter_by(name="Upper Chest").first()
    lower_chest = MuscleGroup.query.filter_by(name="Lower Chest").first()
    
    upper_back = MuscleGroup.query.filter_by(name="Upper Back").first()
    lower_back = MuscleGroup.query.filter_by(name="Lower Back").first()
    lats = MuscleGroup.query.filter_by(name="Lats").first()
    traps = MuscleGroup.query.filter_by(name="Traps").first()

    front_delts = MuscleGroup.query.filter_by(name="Front Delts").first()
    side_delts = MuscleGroup.query.filter_by(name="Side Delts").first()
    rear_delts = MuscleGroup.query.filter_by(name="Rear Delts").first()

    biceps = MuscleGroup.query.filter_by(name="Biceps").first()
    triceps = MuscleGroup.query.filter_by(name="Triceps").first()

    quads = MuscleGroup.query.filter_by(name="Quads").first()
    hamstrings = MuscleGroup.query.filter_by(name="Hamstrings").first()
    glutes = MuscleGroup.query.filter_by(name="Glutes").first()
    calves = MuscleGroup.query.filter_by(name="Calves").first()

    # Add equipment
    equipment = [
        Equipment(name="Barbell"),
        Equipment(name="Dumbbell"),
        Equipment(name="Bodyweight"),
        Equipment(name="Machine"),
        Equipment(name="Cable")
    ]
    db.session.add_all(equipment)
    db.session.commit()

    # Get equipment for exercises
    barbell = Equipment.query.filter_by(name="Barbell").first()
    dumbbell = Equipment.query.filter_by(name="Dumbbell").first()
    bodyweight = Equipment.query.filter_by(name="Bodyweight").first()
    machine = Equipment.query.filter_by(name="Machine").first()
    cable = Equipment.query.filter_by(name="Cable").first()

    # Add exercises
    exercises = [
        # Horizontal Incline Push (Compound)
        Exercise(name="Incline Barbell Bench Press", role=horizontal_incline_push, equipment=barbell, primary_muscles=[upper_chest], secondary_muscles=[front_delts, triceps]),
        Exercise(name="Incline Dumbbell Press", role=horizontal_incline_push, equipment=dumbbell, primary_muscles=[upper_chest], secondary_muscles=[front_delts, triceps]),
        Exercise(name="Decline Push-Ups", role=horizontal_incline_push, equipment=bodyweight, primary_muscles=[upper_chest], secondary_muscles=[front_delts, triceps]),
        Exercise(name="Incline Machine Press", role=horizontal_incline_push, equipment=machine, primary_muscles=[upper_chest], secondary_muscles=[front_delts, triceps]),
        Exercise(name="Smith Incline Bench Press", role=horizontal_incline_push, equipment=machine, primary_muscles=[upper_chest], secondary_muscles=[front_delts, triceps]),

        # Horizontal Push (Compound)
        Exercise(name="Flat Barbell Bench Press", role=horizontal_push, equipment=barbell, primary_muscles=[lower_chest], secondary_muscles=[triceps, front_delts]),
        Exercise(name="Flat Dumbbell Press", role=horizontal_push, equipment=dumbbell, primary_muscles=[lower_chest], secondary_muscles=[triceps, front_delts]),
        Exercise(name="Push-Ups", role=horizontal_push, equipment=bodyweight, primary_muscles=[lower_chest], secondary_muscles=[triceps, front_delts]),
        Exercise(name="Machine Chest Press", role=horizontal_push, equipment=machine, primary_muscles=[lower_chest], secondary_muscles=[triceps, front_delts]),
        Exercise(name="Smith Flat Bench Press", role=horizontal_push, equipment=machine, primary_muscles=[lower_chest], secondary_muscles=[triceps, front_delts]),

        # Vertical Push (Compound)
        Exercise(name="Overhead Barbell Press", role=vertical_push, equipment=barbell, primary_muscles=[front_delts], secondary_muscles=[triceps, upper_chest, side_delts]),
        Exercise(name="Dumbbell Shoulder Press", role=vertical_push, equipment=dumbbell, primary_muscles=[front_delts], secondary_muscles=[triceps, upper_chest, side_delts]),
        Exercise(name="Pike Push-Ups", role=vertical_push, equipment=bodyweight, primary_muscles=[front_delts], secondary_muscles=[triceps, upper_chest, side_delts]),
        Exercise(name="Machine Shoulder Press", role=vertical_push, equipment=machine, primary_muscles=[front_delts], secondary_muscles=[triceps, upper_chest, side_delts]),

        # Side Delt Isolation
        Exercise(name="Dumbbell Lateral Raise", role=side_delt_isolation, equipment=dumbbell, primary_muscles=[side_delts], secondary_muscles=[]),
        Exercise(name="Cable Lateral Raise", role=side_delt_isolation, equipment=cable, primary_muscles=[side_delts], secondary_muscles=[]),
        Exercise(name="Machine Lateral Raise", role=side_delt_isolation, equipment=machine, primary_muscles=[side_delts], secondary_muscles=[]),

        # Tricep Isolation
        Exercise(name="Barbell Skull Crushers", role=tricep_isolation, equipment=barbell, primary_muscles=[triceps], secondary_muscles=[]),
        Exercise(name="Dumbbell Skull Crushers", role=tricep_isolation, equipment=dumbbell, primary_muscles=[triceps], secondary_muscles=[]),
        Exercise(name="Tricep Dips", role=tricep_isolation, equipment=bodyweight, primary_muscles=[triceps], secondary_muscles=[lower_chest, front_delts]),
        Exercise(name="Tricep Pushdown", role=tricep_isolation, equipment=cable, primary_muscles=[triceps], secondary_muscles=[]),
        Exercise(name="Cable Tricep Kickbacks", role=tricep_isolation, equipment=cable, primary_muscles=[triceps], secondary_muscles=[]),

        # Horizontal Pull (Compound)
        Exercise(name="Barbell Row", role=horizontal_pull, equipment=barbell, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),
        Exercise(name="Dumbbell Row", role=horizontal_pull, equipment=dumbbell, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),
        Exercise(name="Single Arm Dumbbell Row", role=horizontal_pull, equipment=dumbbell, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),
        Exercise(name="Inverted Row", role=horizontal_pull, equipment=bodyweight, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),
        Exercise(name="Chest-Supported Machine Row", role=horizontal_pull, equipment=machine, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),
        Exercise(name="Seated Cable Row", role=horizontal_pull, equipment=machine, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),
        Exercise(name="T-Bar Row", role=horizontal_pull, equipment=machine, primary_muscles=[upper_back, traps], secondary_muscles=[rear_delts, lats, biceps]),

        # Vertical Pull (Compound)
        Exercise(name="Pull-Ups", role=vertical_pull, equipment=bodyweight, primary_muscles=[lats], secondary_muscles=[biceps, rear_delts, upper_back]),
        Exercise(name="Chin-Ups", role=vertical_pull, equipment=bodyweight, primary_muscles=[lats, biceps], secondary_muscles=[rear_delts, upper_back]),
        Exercise(name="Lat Pulldown", role=vertical_pull, equipment=machine, primary_muscles=[lats], secondary_muscles=[biceps, rear_delts, upper_back]),
        Exercise(name="Kneeling Lat Pulldown", role=vertical_pull, equipment=cable, primary_muscles=[lats], secondary_muscles=[biceps, rear_delts]),

        # Rear Delt Isolation
        Exercise(name="Dumbbell Rear Delt Fly", role=rear_delt_isolation, equipment=dumbbell, primary_muscles=[rear_delts], secondary_muscles=[]),
        Exercise(name="Reverse Pec Deck", role=rear_delt_isolation, equipment=machine, primary_muscles=[rear_delts], secondary_muscles=[]),
        Exercise(name="Cable Rear Delt Fly", role=rear_delt_isolation, equipment=cable, primary_muscles=[rear_delts], secondary_muscles=[]),
        Exercise(name="Face Pulls", role=rear_delt_isolation, equipment=cable, primary_muscles=[rear_delts], secondary_muscles=[traps]),
        Exercise(name="Ring Face Pulls", role=rear_delt_isolation, equipment=bodyweight, primary_muscles=[rear_delts], secondary_muscles=[traps]),

        # Bicep Isolation
        Exercise(name="Barbell Curl", role=bicep_isolation, equipment=barbell, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Dumbbell Curl", role=bicep_isolation, equipment=dumbbell, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Dumbbell Incline Curl", role=bicep_isolation, equipment=dumbbell, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Preacher Curl", role=bicep_isolation, equipment=dumbbell, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Dumbbell Hammer Curl", role=bicep_isolation, equipment=dumbbell, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Machine Preacher Curl", role=bicep_isolation, equipment=machine, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Cable Hammer Curl", role=bicep_isolation, equipment=cable, primary_muscles=[biceps], secondary_muscles=[]),
        Exercise(name="Bayesian Curl", role=bicep_isolation, equipment=cable, primary_muscles=[biceps], secondary_muscles=[]),

        # Lat Isolation
        Exercise(name="Straight Arm Lat Pulldown", role=lat_isolation, equipment=cable, primary_muscles=[lats], secondary_muscles=[]),
        Exercise(name="Machine Lat Pullover", role=lat_isolation, equipment=machine, primary_muscles=[lats], secondary_muscles=[]),
        Exercise(name="Front Lever Raise", role=lat_isolation, equipment=bodyweight, primary_muscles=[lats], secondary_muscles=[]),

        # Squat (Compound)
        Exercise(name="Barbell Squat", role=squat, equipment=barbell, primary_muscles=[quads, glutes], secondary_muscles=[hamstrings]),
        Exercise(name="Front Squat", role=squat, equipment=barbell, primary_muscles=[quads], secondary_muscles=[glutes]),
        Exercise(name="Hack Squat", role=squat, equipment=machine, primary_muscles=[quads], secondary_muscles=[glutes]),
        Exercise(name="Smith Squat", role=squat, equipment=machine, primary_muscles=[quads], secondary_muscles=[glutes]),
        Exercise(name="Leg Press", role=squat, equipment=machine, primary_muscles=[quads], secondary_muscles=[glutes]),
        Exercise(name="Bulgarian Split Squat", role=squat, equipment=dumbbell, primary_muscles=[quads], secondary_muscles=[glutes, hamstrings]),

        # Hinge (Compound)
        Exercise(name="Barbell Deadlift", role=hinge, equipment=barbell, primary_muscles=[glutes, lower_back], secondary_muscles=[hamstrings, quads]),
        Exercise(name="Barbell Romanian Deadlift", role=hinge, equipment=barbell, primary_muscles=[hamstrings], secondary_muscles=[glutes, lower_back]),
        Exercise(name="Barbell Stiff Leg Deadlift", role=hinge, equipment=barbell, primary_muscles=[hamstrings, lower_back], secondary_muscles=[glutes, quads]),
        Exercise(name="Good Mornings", role=hinge, equipment=barbell, primary_muscles=[hamstrings, lower_back], secondary_muscles=[glutes]),
        Exercise(name="Dumbbell Romanian Deadlift", role=hinge, equipment=dumbbell, primary_muscles=[hamstrings], secondary_muscles=[glutes]),
        Exercise(name="Barbell Hip Thrust", role=hinge, equipment=barbell, primary_muscles=[glutes], secondary_muscles=[hamstrings]),
        Exercise(name="Machine Hip Thrust", role=hinge, equipment=machine, primary_muscles=[glutes], secondary_muscles=[hamstrings]),
        Exercise(name="Back Extension", role=hinge, equipment=bodyweight, primary_muscles=[glutes, lower_back], secondary_muscles=[hamstrings]),

        # Quad Isolation
        Exercise(name="Leg Extensions", role=quad_isolation, equipment=machine, primary_muscles=[quads], secondary_muscles=[]),
        Exercise(name="Sissy Squats", role=quad_isolation, equipment=bodyweight, primary_muscles=[quads], secondary_muscles=[]),
        Exercise(name="Adduction Machine", role=quad_isolation, equipment=machine, primary_muscles=[quads], secondary_muscles=[]),
        Exercise(name="Reverse Nordic Curl", role=quad_isolation, equipment=bodyweight, primary_muscles=[quads], secondary_muscles=[]),

        # Hamstring Isolation
        Exercise(name="Lying Hamstring Curl", role=hamstring_isolation, equipment=machine, primary_muscles=[hamstrings], secondary_muscles=[]),
        Exercise(name="Seated Hamstring Curl", role=hamstring_isolation, equipment=machine, primary_muscles=[hamstrings], secondary_muscles=[]),
        Exercise(name="Nordic Curl", role=hamstring_isolation, equipment=bodyweight, primary_muscles=[hamstrings], secondary_muscles=[]),

        # Calf Isolation
        Exercise(name="Standing Calf Raise", role=calf_isolation, equipment=machine, primary_muscles=[calves], secondary_muscles=[]),
        Exercise(name="Seated Calf Raise", role=calf_isolation, equipment=machine, primary_muscles=[calves], secondary_muscles=[]),
        Exercise(name="Leg Press Calf Raise", role=calf_isolation, equipment=machine, primary_muscles=[calves], secondary_muscles=[]),
        Exercise(name="Barbell Calf Raise", role=calf_isolation, equipment=barbell, primary_muscles=[calves], secondary_muscles=[]),
        Exercise(name="Calf Raise", role=calf_isolation, equipment=dumbbell, primary_muscles=[calves], secondary_muscles=[]),
    ]

    db.session.add_all(exercises)
    db.session.commit()


def handle_populate():
        clear()
        populate()
        print("\nDATABASE POPULATED\n")


if __name__ == "__main__":
    with app.app_context():
        handle_populate()
