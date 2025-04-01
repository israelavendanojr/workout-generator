from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        # get preferences from form
        days_available = int(request.form.get("days_available"))
        equipment = request.form.getlist("equipment")

        # validate preferences
        if days_available < 1 or 6 < days_available:
            flash('Days per week must be within 1-6', category='error')
        elif len(equipment) < 1:
            flash('Must fill equipment field', category='error')
        else:
            generate_plan(days_available, equipment)
            flash('Generated workout plan!', category='success')

    return render_template("home.html")

def generate_plan(days_available, equipment):
    from website import db
    from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association

    # Find workout splits
    workout_splits = WorkoutSplit.query.filter_by(days_per_week=days_available).all()
    
    print("\nSUITABLE SPLITS FOR", days_available, "DAYS A WEEK\n", "WITH EQUIPMENT: ", equipment)
    
    # generate plan for each workout split
    for split in workout_splits:
        print("STRUCTURE OF SPLIT: ", split.name + "\n")
        
        # get workout day from split
        for day in split.workout_days:
            print(day.name)

            ordered_roles = (
                db.session.query(ExerciseRole)
                .join(day_role_association)
                .filter(day_role_association.c.workout_day_id == day.id)
                .order_by(day_role_association.c.order)  # Order by the 'order' column in the association table
                .all()
            )

            # find suitable exercises based on exercise role and equipment available
            for role in ordered_roles:
                print("ROLE: ", role.role)
                exercises = (
                    db.session.query(Exercise)
                    .filter(Exercise.role_id == role.id)
                    .all()
                )

                for exercise in exercises:
                    print(exercise.name)
                print("\n")

            print("\n")
