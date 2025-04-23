from website import create_app, db
from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association, ExerciseType, EquipmentType, MuscleGroup, primary_muscle_association, secondary_muscle_association

app = create_app()

# clears database
def clear():
    # Delete associations to prevent foreign key errors
    db.session.query(day_role_association).delete()
    db.session.query(split_day_association).delete()
    db.session.query(primary_muscle_association).delete()
    db.session.query(secondary_muscle_association).delete()

    # Then delete the main tables
    db.session.query(WorkoutSplit).delete()
    db.session.query(WorkoutDay).delete()
    db.session.query(ExerciseRole).delete()
    db.session.query(Exercise).delete()
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

# def add_equipment_to_exercise(exercise, equipment_list):
#     for equipment in equipment_list:
#         db.session.execute(exercise_equipment_association.insert().values(
#             exercise_id=exercise.id,
#             equipment_id=equipment.id
#         ))
#     db.session.commit()

def populate():
    # Create workout days
    full_A = WorkoutDay(name="Full Body")
    full_B = WorkoutDay(name="Full Body")
    full_C = WorkoutDay(name="Full Body")

    # Add muscle groups
    muscle_groups = [
        MuscleGroup(name="Upper Chest"),
        MuscleGroup(name="Lower Chest"),
        MuscleGroup(name="Upper Back"),
        MuscleGroup(name="Lower Back"),
        MuscleGroup(name="Lats"),
        MuscleGroup(name="Traps"),
        MuscleGroup(name="Front Delts"),
        MuscleGroup(name="Side Delts"),
        MuscleGroup(name="Rear Delts"),
        MuscleGroup(name="Biceps"),
        MuscleGroup(name="Triceps"),
        MuscleGroup(name="Quads"),
        MuscleGroup(name="Hamstrings"),
        MuscleGroup(name="Glutes"),
        MuscleGroup(name="Calves")
    ]
    db.session.add_all(muscle_groups)
    db.session.commit()

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

    # Add exercises
    exercises = [
        # Horizontal Incline Push (Compound)
        Exercise(name="Incline Barbell Bench Press", role=horizontal_incline_push, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Upper Chest"], secondary=["Front Delts", "Triceps"]),
        Exercise(name="Incline Dumbbell Press", role=horizontal_incline_push, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Upper Chest"], secondary=["Front Delts", "Triceps"]),
        Exercise(name="Decline Push-Ups", role=horizontal_incline_push, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Upper Chest"], secondary=["Front Delts", "Triceps"]),
        Exercise(name="Incline Machine Press", role=horizontal_incline_push, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Upper Chest"], secondary=["Front Delts", "Triceps"]),
        Exercise(name="Smith Incline Bench Press", role=horizontal_incline_push, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Upper Chest"], secondary=["Front Delts", "Triceps"]),

        # Horizontal Push (Compound)
        Exercise(name="Flat Barbell Bench Press", role=horizontal_push, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Chest"], secondary=["Triceps", "Front Delts"]),
        Exercise(name="Flat Dumbbell Press", role=horizontal_push, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Chest"], secondary=["Triceps", "Front Delts"]),
        Exercise(name="Push-Ups", role=horizontal_push, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Chest"], secondary=["Triceps", "Front Delts"]),
        Exercise(name="Machine Chest Press", role=horizontal_push, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Chest"], secondary=["Triceps", "Front Delts"]),
        Exercise(name="Smith Flat Bench Press", role=horizontal_push, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Chest"], secondary=["Triceps", "Front Delts"]),

        # Vertical Push (Compound)
        Exercise(name="Overhead Barbell Press", role=vertical_push, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Front Delts"], secondary=["Triceps", "Upper Chest", "Side Delts"]),
        Exercise(name="Dumbbell Shoulder Press", role=vertical_push, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Front Delts"], secondary=["Triceps", "Upper Chest", "Side Delts"]),
        Exercise(name="Pike Push-Ups", role=vertical_push, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Front Delts"], secondary=["Triceps", "Upper Chest", "Side Delts"]),
        Exercise(name="Machine Shoulder Press", role=vertical_push, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Front Delts"], secondary=["Triceps", "Upper Chest", "Side Delts"]),

        # Side Delt Isolation
        Exercise(name="Dumbbell Lateral Raise", role=side_delt_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Side Delts"], secondary=[]),
        Exercise(name="Cable Lateral Raise", role=side_delt_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Side Delts"], secondary=[]),
        Exercise(name="Machine Lateral Raise", role=side_delt_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Side Delts"], secondary=[]),

        # Tricep Isolation
        Exercise(name="Barbell Skull Crushers", role=tricep_isolation, equipment=EquipmentType.BARBELL, type=ExerciseType.ISOLATION, primary=["Triceps"], secondary=[]),
        Exercise(name="Dumbbell Skull Crushers", role=tricep_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Triceps"], secondary=[]),
        Exercise(name="Tricep Dips", role=tricep_isolation, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.ISOLATION, primary=["Triceps"], secondary=["Chest", "Front Delts"]),
        Exercise(name="Tricep Pushdown", role=tricep_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Triceps"], secondary=[]),
        Exercise(name="Cable Tricep Kickbacks", role=tricep_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Triceps"], secondary=[]),

        # Horizontal Pull (Compound)
        Exercise(name="Barbell Row", role=horizontal_pull, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Lats", "Mid Traps"], secondary=["Rear Delts", "Biceps"]),
        Exercise(name="Dumbbell Row", role=horizontal_pull, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Lats", "Mid Traps"], secondary=["Rear Delts", "Biceps"]),
        Exercise(name="Single Arm Dumbbell Row", role=horizontal_pull, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Lats"], secondary=["Rear Delts", "Biceps"]),
        Exercise(name="Inverted Row", role=horizontal_pull, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Lats", "Upper Back"], secondary=["Biceps", "Rear Delts"]),
        Exercise(name="Chest-Supported Machine Row", role=horizontal_pull, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Mid Traps"], secondary=["Biceps", "Rear Delts"]),
        Exercise(name="Seated Cable Row", role=horizontal_pull, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Lats", "Mid Traps"], secondary=["Biceps"]),
        Exercise(name="T-Bar Row", role=horizontal_pull, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Lats", "Mid Traps"], secondary=["Biceps", "Rear Delts"]),

        # Vertical Pull (Compound)
        Exercise(name="Pull-Ups", role=vertical_pull, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Lats"], secondary=["Biceps", "Rear Delts"]),
        Exercise(name="Chin-Ups", role=vertical_pull, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Lats", "Biceps"], secondary=["Rear Delts"]),
        Exercise(name="Lat Pulldown", role=vertical_pull, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Lats"], secondary=["Biceps", "Rear Delts"]),
        Exercise(name="Kneeling Lat Pulldown", role=vertical_pull, equipment=EquipmentType.CABLE, type=ExerciseType.COMPOUND, primary=["Lats"], secondary=["Biceps"]),

        # Rear Delt Isolation
        Exercise(name="Dumbbell Rear Delt Fly", role=rear_delt_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Rear Delts"], secondary=[]),
        Exercise(name="Reverse Pec Deck", role=rear_delt_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Rear Delts"], secondary=[]),
        Exercise(name="Cable Rear Delt Fly", role=rear_delt_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Rear Delts"], secondary=[]),
        Exercise(name="Face Pulls", role=rear_delt_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Rear Delts", "Mid Traps"], secondary=[]),
        Exercise(name="Ring Face Pulls", role=rear_delt_isolation, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.ISOLATION, primary=["Rear Delts", "Mid Traps"], secondary=[]),

        # Bicep Isolation
        Exercise(name="Barbell Curl", role=bicep_isolation, equipment=EquipmentType.BARBELL, type=ExerciseType.ISOLATION, primary=["Biceps"], secondary=[]),
        Exercise(name="Dumbbell Curl", role=bicep_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Biceps"], secondary=[]),
        Exercise(name="Dumbbell Incline Curl", role=bicep_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Biceps (Long Head)"], secondary=[]),
        Exercise(name="Preacher Curl", role=bicep_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Biceps (Short Head)"], secondary=[]),
        Exercise(name="Dumbbell Hammer Curl", role=bicep_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Biceps", "Brachialis"], secondary=[]),
        Exercise(name="Machine Preacher Curl", role=bicep_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Biceps"], secondary=[]),
        Exercise(name="Cable Hammer Curl", role=bicep_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Biceps", "Brachialis"], secondary=[]),
        Exercise(name="Bayesian Curl", role=bicep_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Biceps (Long Head)"], secondary=[]),

        # Lat Isolation
        Exercise(name="Straight Arm Lat Pulldown", role=lat_isolation, equipment=EquipmentType.CABLE, type=ExerciseType.ISOLATION, primary=["Lats"], secondary=[]),
        Exercise(name="Machine Lat Pullover", role=lat_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Lats"], secondary=[]),
        Exercise(name="Front Lever Raise", role=lat_isolation, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.ISOLATION, primary=["Lats"], secondary=["Core"]),

        # Squat (Compound)
        Exercise(name="Barbell Squat", role=squat, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Quads", "Glutes"], secondary=["Hamstrings", "Core"]),
        Exercise(name="Front Squat", role=squat, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Quads"], secondary=["Glutes", "Core"]),
        Exercise(name="Hack Squat", role=squat, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Quads"], secondary=["Glutes"]),
        Exercise(name="Smith Squat", role=squat, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Quads"], secondary=["Glutes"]),
        Exercise(name="Leg Press", role=squat, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Quads"], secondary=["Glutes"]),
        Exercise(name="Bulgarian Split Squat", role=squat, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Quads"], secondary=["Glutes", "Hamstrings"]),

        # Hinge (Compound)
        Exercise(name="Barbell Deadlift", role=hinge, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Glutes", "Hamstrings"], secondary=["Lats", "Core"]),
        Exercise(name="Barbell Romanian Deadlift", role=hinge, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Hamstrings"], secondary=["Glutes", "Lower Back"]),
        Exercise(name="Good Mornings", role=hinge, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Hamstrings", "Lower Back"], secondary=["Glutes"]),
        Exercise(name="Dumbbell Romanian Deadlift", role=hinge, equipment=EquipmentType.DUMBBELL, type=ExerciseType.COMPOUND, primary=["Hamstrings"], secondary=["Glutes"]),
        Exercise(name="Barbell Hip Thrust", role=hinge, equipment=EquipmentType.BARBELL, type=ExerciseType.COMPOUND, primary=["Glutes"], secondary=["Hamstrings"]),
        Exercise(name="Machine Hip Thrust", role=hinge, equipment=EquipmentType.MACHINE, type=ExerciseType.COMPOUND, primary=["Glutes"], secondary=["Hamstrings"]),
        Exercise(name="Back Extension", role=hinge, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.COMPOUND, primary=["Glutes", "Lower Back"], secondary=["Hamstrings"]),

        # Quad Isolation
        Exercise(name="Leg Extensions", role=quad_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Quads"], secondary=[]),
        Exercise(name="Sissy Squats", role=quad_isolation, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.ISOLATION, primary=["Quads"], secondary=[]),
        Exercise(name="Adduction Machine", role=quad_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Adductors"], secondary=[]),
        Exercise(name="Reverse Nordic Curl", role=quad_isolation, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.ISOLATION, primary=["Quads"], secondary=[]),

        # Hamstring Isolation
        Exercise(name="Lying Hamstring Curl", role=hamstring_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Hamstrings"], secondary=[]),
        Exercise(name="Seated Hamstring Curl", role=hamstring_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Hamstrings"], secondary=[]),
        Exercise(name="Nordic Curl", role=hamstring_isolation, equipment=EquipmentType.BODYWEIGHT, type=ExerciseType.ISOLATION, primary=["Hamstrings"], secondary=[]),

        # Calf Isolation
        Exercise(name="Standing Calf Raise", role=calf_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Calves"], secondary=[]),
        Exercise(name="Seated Calf Raise", role=calf_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Calves"], secondary=[]),
        Exercise(name="Leg Press Calf Raise", role=calf_isolation, equipment=EquipmentType.MACHINE, type=ExerciseType.ISOLATION, primary=["Calves"], secondary=[]),
        Exercise(name="Barbell Calf Raise", role=calf_isolation, equipment=EquipmentType.BARBELL, type=ExerciseType.ISOLATION, primary=["Calves"], secondary=[]),
        Exercise(name="Calf Raise", role=calf_isolation, equipment=EquipmentType.DUMBBELL, type=ExerciseType.ISOLATION, primary=["Calves"], secondary=[]),
    ]

    # Add all exercises to the database
    db.session.add_all(exercises)
    db.session.commit()


def handle_populate():
        clear()
        populate()
        print("\nDATABASE POPULATED\n")


if __name__ == "__main__":
    with app.app_context():
        handle_populate()
