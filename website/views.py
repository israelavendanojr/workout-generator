from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        # get preferences from form
        days_available = int(request.form.get("days_available"))
        # session_length = request.form.get("session_length")
        # goal = request.form.get("goal")
        equipment = request.form.getlist("equipment")

        # validate preferences
        if days_available < 1 or 6 < days_available:
            flash('Days per week must be within 1-6', category='error')
        # elif not session_length:
        #     flash('Session length field required', category='error')
        # elif not goal:
        #     flash('Goal field required', category='error')
        elif len(equipment) < 1:
            flash('Must fill equipment field', category='error')
        else:
            generate_plan(days_available, equipment)
            flash('Generated workout plan!', category='success')

    return render_template("home.html")

def generate_plan(days_available, equipment):
    from website import db
    from .models import WorkoutSplit, WorkoutDay, ExerciseRole, day_role_association

    # Find workout split
    workout_splits = WorkoutSplit.query.filter_by(days_per_week=days_available).all()
    
    print("\nSUITABLE SPLITS FOR", days_available, "DAYS A WEEK\n")
    
    for split in workout_splits:
        print("STRUCTURE OF SPLIT: ", split.name + "\n")
        
        for day in split.workout_days:
            print(day.name)

            # Get the exercises for the workout day, ordered by the 'order' in the association table
            ordered_roles = (
                db.session.query(ExerciseRole)
                .join(day_role_association)
                .filter(day_role_association.c.workout_day_id == day.id)
                .order_by(day_role_association.c.order)  # Order by the 'order' column in the association table
                .all()
            )

            # Print role names in order
            for role in ordered_roles:
                print(role.role)

            print("\n")
    # generate plan for each split
    for split in workout_splits:
        pass
