from website import create_app, db
from website.models import WorkoutSplit, WorkoutDay, ExerciseRole, Exercise

app = create_app()

def clear():
    with app.app_context():
        db.session.query(WorkoutSplit).delete()
        db.session.query(WorkoutDay).delete()
        db.session.query(ExerciseRole).delete()
        db.session.query(Exercise).delete()
        db.session.commit()

def populate():
    with app.app_context():
        # create workout days
        full_A = WorkoutDay(name="Full Body")
        full_B = WorkoutDay(name="Full Body")
        full_C = WorkoutDay(name="Full Body")

        upper_A = WorkoutDay(name="Upper")
        lower_A = WorkoutDay(name="Lower")
        upper_B = WorkoutDay(name="Upper")
        lower_B = WorkoutDay(name="Lower")


        push_A = WorkoutDay(name="Push")
        pull_A = WorkoutDay(name="Pull")
        push_B = WorkoutDay(name="Push")
        legs_A = WorkoutDay(name="Legs")
        pull_B = WorkoutDay(name="Pull")
        legs_B = WorkoutDay(name="Legs")

        chestback_A = WorkoutDay(name="Chest + Back")
        chestback_B = WorkoutDay(name="Chest + Back")
        arms_A = WorkoutDay(name="Arms")
        arms_B = WorkoutDay(name="Arms")

        db.session.add_all([full_A, full_B, full_C, 
                            upper_A, lower_A, upper_B, lower_B,
                            push_A, pull_A, legs_A, push_B, pull_B, legs_B,
                            chestback_A, chestback_B, arms_A, arms_B])

        # create workout splits
        fb1 = WorkoutSplit(name="Full Body", days_per_week="1", workout_days=[full_A])

        fb2 = WorkoutSplit(name="Full Body", days_per_week="2", workout_days=[full_A, full_B])

        fb3 = WorkoutSplit(name="Full Body", days_per_week="3", workout_days=[full_A, full_B, full_C])
        ul_fb = WorkoutSplit(name="Upper Lower + Full Body", days_per_week="3", workout_days=[upper_A, lower_A, full_A])    
        
        ul = WorkoutSplit(name="Upper Lower", days_per_week="4", workout_days=[upper_A, lower_A, upper_B, lower_B])
        # pp = WorkoutSplit(name="Push Pull", days_per_week="4")

        ppl_ul = WorkoutSplit(name="Push Pull Legs + Upper Lower", days_per_week="5", workout_days=[push_A, pull_A, legs_A, upper_A, lower_A])
        arnold_ul = WorkoutSplit(name="Arnold + Upper Lower", days_per_week="5", workout_days=[chestback_A, arms_A, legs_A, upper_A, lower_A])
        ul_arms = WorkoutSplit(name="Upper Lower + Arms", days_per_week="5", workout_days=[upper_A, lower_A, upper_B, lower_B, arms_A])

        ppl = WorkoutSplit(name="Push Pull Legs", days_per_week="6", workout_days=[push_A, pull_A, legs_A, push_B, pull_B, legs_B])
        arnold = WorkoutSplit(name="Arnold", days_per_week="6", workout_days=[chestback_A, arms_A, legs_A, chestback_B, arms_B, legs_B])
        ppl_arnold = WorkoutSplit(name="Push Pull Legs + Arnold", days_per_week="6", workout_days=[push_A, pull_A, legs_A, chestback_A, arms_A, legs_A])

        db.session.add_all([fb1,
                            fb2,
                            fb3,ul_fb,
                            ul,
                            ppl_ul,arnold_ul,ul_arms,
                            ppl,arnold,ppl_arnold])

        # 


        db.session.commit()

if __name__ == "__main__":
    clear()
    populate()
    print("\nDATEBASE POPULATED\n")