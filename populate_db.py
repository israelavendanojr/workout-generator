from website import create_app, db
from website.models import WorkoutSplit, WorkoutDay, split_day_association

app = create_app()

def clear():
    with app.app_context():
        db.session.query(WorkoutSplit).delete()
        db.session.query(WorkoutDay).delete()
        db.session.commit()

def add_split(name, days_per_week, workout_days):
    """ Adds a WorkoutSplit and ensures workout days are stored in order """
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
    return split

def populate():
    with app.app_context():
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

if __name__ == "__main__":
    clear()
    populate()
    print("\nDATABASE POPULATED\n")
