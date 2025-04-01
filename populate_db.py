from website import create_app, db
from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association

app = create_app()

# clears database
def clear():
    with app.app_context():
        # First delete associations to prevent foreign key errors
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
def add_exercises_to_day(workout_day, exercises):
    # Add exercises to the day with the correct order
    for index, exercise in enumerate(exercises):
        db.session.execute(day_role_association.insert().values(
            workout_day_id=workout_day.id,
            exercise_role_id=exercise.id,
            order=index  # Ensures the order is maintained
        ))

    db.session.commit()

def populate():
    with app.app_context():
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

        # Add exercises to each day with the correct order
        add_exercises_to_day(push_A, [
            horizontal_incline_push, 
            horizontal_push, 
            vertical_push, 
            side_delt_isolation, 
            tricep_isolation
        ])
        
        add_exercises_to_day(pull_A, [
            vertical_pull, 
            horizontal_pull, 
            lat_isolation, 
            rear_delt_isolation, 
            bicep_isolation
        ])
        
        add_exercises_to_day(legs_A, [
            squat, 
            hinge, 
            quad_isolation, 
            hamstring_isolation, 
            calf_isolation
        ])
        
        add_exercises_to_day(push_B, [
            vertical_push, 
            side_delt_isolation, 
            horizontal_incline_push, 
            horizontal_push, 
            tricep_isolation
        ])
        
        add_exercises_to_day(pull_B, [
            vertical_pull, 
            horizontal_pull, 
            lat_isolation, 
            rear_delt_isolation, 
            bicep_isolation
        ])
        
        add_exercises_to_day(legs_B, [
            squat, 
            hinge, 
            quad_isolation, 
            hamstring_isolation, 
            calf_isolation
        ])

        add_exercises_to_day(upper_A, [
            horizontal_incline_push, 
            vertical_pull, 
            horizontal_push, 
            horizontal_pull, 
            side_delt_isolation, 
            bicep_isolation, 
            tricep_isolation
        ])
        
        add_exercises_to_day(lower_A, [
            squat, 
            hinge, 
            quad_isolation, 
            hamstring_isolation, 
            calf_isolation
        ])
        
        add_exercises_to_day(upper_B, [
            horizontal_incline_push, 
            vertical_pull, 
            horizontal_push, 
            horizontal_pull, 
            rear_delt_isolation, 
            bicep_isolation, 
            tricep_isolation
        ])
        
        add_exercises_to_day(lower_B, [
            squat, 
            hinge, 
            quad_isolation, 
            hamstring_isolation, 
            calf_isolation
        ])


if __name__ == "__main__":
    clear()
    populate()
    print("\nDATABASE POPULATED\n")
