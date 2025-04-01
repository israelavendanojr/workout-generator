from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
import json


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
            workout_plans = generate_plans(days_available, equipment)
            flash('Generated workout plan!', category='success')

            # session to store across requests, convert to json bc session can only store simple types
            session['workout_plans'] = json.dumps(workout_plans)
            return redirect(url_for('views.display_plans'))


    return render_template("home.html")

@views.route('/display_plans')
def display_plans():
    # Retrieve the workout plan from session
    workout_plans_json = session.get('workout_plans')

    if not workout_plans_json:
        flash("No workout plan found. Please generate a plan first.", category='error')
        return redirect(url_for('views.home'))
    
    try:
        # convert back into list of dictionary for usage
        workout_plans = json.loads(workout_plans_json)
    except Exception as e:
        flash(f"Error decoding workout plans: {str(e)}", category='error')
        return redirect(url_for('views.home'))
    
    return render_template("display_plans.html", plans=workout_plans)

def generate_plans(days_available, equipment):
    from website import db
    from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association
    import random

    # Dictionary to store plan information
    workout_plans = []

    # Find workout splits
    workout_splits = WorkoutSplit.query.filter_by(days_per_week=days_available).all()
    
    print("\nSUITABLE SPLITS FOR", days_available, "DAYS A WEEK\n", "WITH EQUIPMENT: ", equipment)
    
    # generate plan for each workout split
    for split in workout_splits:

        # insert split name into dictionary and establish workout days
        plan = {
            "split_name": split.name,
            "days": []
        }

        print("STRUCTURE OF SPLIT: ", split.name + "\n")
        
        # get workout day from split
        for day in split.workout_days:
            print(day.name)

            # insert day name into dictionary and establish exercises
            day_info = {
                "name": day.name,
                "exercises": []
            }

            ordered_roles = (
                db.session.query(ExerciseRole)
                .join(day_role_association)
                .filter(day_role_association.c.workout_day_id == day.id)
                .order_by(day_role_association.c.order)  # Order by the 'order' column in the association table
                .all()
            )

            # find suitable exercises based on exercise role and equipment available
            for role in ordered_roles:
                # print("ROLE: ", role.role)
                exercises = (
                    db.session.query(Exercise)
                    .filter(Exercise.role_id == role.id)
                    .filter(Exercise.equipment.in_(equipment))
                    .all()
                )

                if exercises:
                    random_index = random.randint(0, len(exercises)-1)
                    random_exercise = exercises[random_index]
                    print(random_exercise.name)

                    # insert exercises into dictionary
                    day_info["exercises"].append({
                        "name": random_exercise.name,
                        "sets": 2,
                        "start_reps": 6,
                        "end_reps": 8
                    })
                else:
                    print("No suitable exercise for ", role.role, " found")
                    # insert null exercise into dictionary if none found
                    null_exercise_message = "No suitable exercise for " + role.role + " found"
                    day_info["exercises"].append({
                        "name": null_exercise_message,
                        "sets": 0,
                        "start_reps": 0,
                        "end_reps": 0
                    })

            # add workout days to current workout plan being constructed
            plan["days"].append(day_info)

            print("\n")

        # add completed workout plan to list of generated plans
        workout_plans.append(plan)

    # return dictionary of all generated plans
    return workout_plans
