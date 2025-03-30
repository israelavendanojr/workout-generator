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
        full = WorkoutDay(name="Full Body")

        upper = WorkoutDay(name="Upper")
        lower = WorkoutDay(name="Lower")

        push = WorkoutDay(name="Push")
        pull = WorkoutDay(name="Pull")
        legs = WorkoutDay(name="Legs")

        chest_back = WorkoutDay(name="Chest + Back")
        arms = WorkoutDay(name="Arms")

        db.session.add_all([push,pull,legs,upper,lower,full])

        # create workout splits
        fb1 = WorkoutSplit(name="Full Body", days_per_week="1", workout_days=[full])

        fb2 = WorkoutSplit(name="Full Body", days_per_week="2", workout_days=[full, full])

        fb3 = WorkoutSplit(name="Full Body", days_per_week="3", workout_days=[full, full, full])
        ul_fb = WorkoutSplit(name="Upper Lower + Full Body", days_per_week="3", workout_days=[upper, lower, full])    
        
        ul = WorkoutSplit(name="Upper Lower", days_per_week="4", workout_days=[upper, lower, upper, lower])
        # pp = WorkoutSplit(name="Push Pull", days_per_week="4")

        ppl_ul = WorkoutSplit(name="Push Pull Legs + Upper Lower", days_per_week="5", workout_days=[push, pull, legs, upper, lower])
        arnold_ul = WorkoutSplit(name="Arnold + Upper Lower", days_per_week="5", workout_days=[chest_back, arms, legs, upper, lower])
        ul_arms = WorkoutSplit(name="Upper Lower + Arms", days_per_week="5", workout_days=[upper, lower, upper, lower, arms])

        ppl = WorkoutSplit(name="Push Pull Legs", days_per_week="6", workout_days=[push, pull, legs, push, pull, legs])
        arnold = WorkoutSplit(name="Arnold", days_per_week="6", workout_days=[chest_back, arms, legs, chest_back, arms, legs])
        ppl_arnold = WorkoutSplit(name="Push Pull Legs + Arnold", days_per_week="6", workout_days=[push, pull, legs, chest_back, arms, legs])

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