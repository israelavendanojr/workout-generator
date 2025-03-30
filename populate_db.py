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
        # create workout splits

        fb1 = WorkoutSplit(name="Full Body", days_per_week="1")

        fb2 = WorkoutSplit(name="Full Body", days_per_week="2")

        fb3 = WorkoutSplit(name="Full Body", days_per_week="3")
        ul_fb = WorkoutSplit(name="Upper Lower + Full Body", days_per_week="3")    
        
        ul = WorkoutSplit(name="Upper Lower", days_per_week="4")

        ppl_ul = WorkoutSplit(name="Push Pull Legs + Upper Lower", days_per_week="5")
        arnold_ul = WorkoutSplit(name="Arnold + Upper Lower", days_per_week="5")
        ul_arms = WorkoutSplit(name="Upper Lower + Arms", days_per_week="5")

        ppl = WorkoutSplit(name="Push Pull Legs", days_per_week="6")
        arnold = WorkoutSplit(name="Arnold", days_per_week="6")
        ppl_arnold = WorkoutSplit(name="Push Pull Legs + Arnold", days_per_week="6")

        db.session.add_all([fb1,fb2,fb3,ul_fb,ul,ppl_ul,arnold_ul,ul_arms,ppl,arnold,ppl_arnold])

        db.session.commit()

if __name__ == "__main__":
    clear()
    populate()
    print("Database populated")